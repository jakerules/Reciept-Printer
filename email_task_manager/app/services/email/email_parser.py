"""
Email parser service for extracting tasks from emails.
"""
import re
import spacy
from datetime import datetime, timedelta
import dateutil.parser
from app import db
from app.models import Task

class EmailParser:
    """Service for parsing emails and extracting tasks."""
    
    def __init__(self, spacy_model='en_core_web_sm', use_openai=False, openai_api_key=None):
        """
        Initialize the email parser.
        
        Args:
            spacy_model: Name of the spaCy model to use
            use_openai: Whether to use OpenAI for parsing
            openai_api_key: OpenAI API key
        """
        self.nlp = spacy.load(spacy_model)
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key
    
    def parse_email(self, email):
        """
        Parse an email and extract tasks.
        
        Args:
            email: Email object to parse
            
        Returns:
            List of extracted tasks
        """
        if self.use_openai and self.openai_api_key:
            return self._parse_with_openai(email)
        else:
            return self._parse_with_rules(email)
    
    def _parse_with_rules(self, email):
        """
        Parse an email using rule-based approach.
        
        Args:
            email: Email object to parse
            
        Returns:
            List of extracted tasks
        """
        tasks = []
        
        # Use the plain text body for parsing
        text = email.body_text or ''
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract potential tasks based on common patterns
        task_candidates = []
        
        # Look for bullet points or numbered lists
        bullet_pattern = r'(?:^|\n)(?:\*|\-|\d+\.)[ \t]+(.*?)(?:\n|$)'
        bullet_matches = re.findall(bullet_pattern, text)
        task_candidates.extend(bullet_matches)
        
        # Look for task-like sentences (containing action verbs)
        action_verbs = ['create', 'update', 'delete', 'review', 'check', 'send', 'prepare', 
                        'complete', 'finish', 'implement', 'develop', 'fix', 'resolve']
        
        for sentence in doc.sents:
            # Check if sentence contains an action verb
            contains_action = any(token.lemma_.lower() in action_verbs for token in sentence)
            if contains_action:
                task_candidates.append(sentence.text)
        
        # Extract dates and times
        dates = []
        for ent in doc.ents:
            if ent.label_ == 'DATE' or ent.label_ == 'TIME':
                dates.append((ent.text, ent.start_char, ent.end_char))
        
        # Create tasks from candidates
        for i, candidate in enumerate(task_candidates):
            # Skip if too short
            if len(candidate.strip()) < 5:
                continue
                
            # Create a new task
            task = Task(
                title=candidate.strip()[:255],  # Limit title length
                description=candidate.strip(),
                email_id=email.id,
                requestor_name=email.sender,
                requestor_email=email.sender_email
            )
            
            # Try to associate a date with this task
            task_due_date = self._extract_due_date(candidate, doc, dates)
            if task_due_date:
                task.due_date = task_due_date
            
            # Extract priority
            priority = self._extract_priority(candidate)
            if priority:
                task.priority = priority
            
            # Extract location if any
            location = self._extract_location(candidate, doc)
            if location:
                task.location = location
            
            tasks.append(task)
        
        # If no tasks were found, create a generic one based on the subject
        if not tasks and email.subject:
            task = Task(
                title=email.subject,
                description=text[:1000] if text else '',  # Limit description length
                email_id=email.id,
                requestor_name=email.sender,
                requestor_email=email.sender_email
            )
            tasks.append(task)
        
        # Save tasks to database
        for task in tasks:
            db.session.add(task)
        
        db.session.commit()
        return tasks
    
    def _parse_with_openai(self, email):
        """
        Parse an email using OpenAI.
        
        Args:
            email: Email object to parse
            
        Returns:
            List of extracted tasks
        """
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            # Prepare the prompt
            prompt = f"""
            Extract tasks from the following email:
            
            From: {email.sender} <{email.sender_email}>
            Subject: {email.subject}
            
            {email.body_text}
            
            For each task, provide:
            1. Task title
            2. Task description
            3. Due date (if mentioned)
            4. Priority (if mentioned)
            5. Location (if mentioned)
            
            Format the response as JSON:
            [
                {{
                    "title": "Task title",
                    "description": "Task description",
                    "due_date": "YYYY-MM-DD" or null,
                    "priority": "Low/Medium/High/Urgent" or null,
                    "location": "Location" or null
                }},
                ...
            ]
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a task extraction assistant. Extract tasks from emails accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse the response
            import json
            content = response.choices[0].message.content
            
            # Extract JSON part from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                tasks_data = json.loads(json_str)
            else:
                # Fallback if JSON extraction fails
                return self._parse_with_rules(email)
            
            # Create Task objects
            tasks = []
            for task_data in tasks_data:
                task = Task(
                    title=task_data.get('title', '')[:255],
                    description=task_data.get('description', ''),
                    email_id=email.id,
                    requestor_name=email.sender,
                    requestor_email=email.sender_email
                )
                
                # Set due date if provided
                due_date_str = task_data.get('due_date')
                if due_date_str:
                    try:
                        task.due_date = dateutil.parser.parse(due_date_str)
                    except:
                        pass
                
                # Set priority if provided
                priority = task_data.get('priority')
                if priority in ['Low', 'Medium', 'High', 'Urgent']:
                    task.priority = priority
                
                # Set location if provided
                location = task_data.get('location')
                if location:
                    task.location = location
                
                tasks.append(task)
                db.session.add(task)
            
            db.session.commit()
            return tasks
            
        except Exception as e:
            print(f"Error using OpenAI for parsing: {str(e)}")
            # Fallback to rule-based parsing
            return self._parse_with_rules(email)
    
    def _extract_due_date(self, text, doc, dates):
        """
        Extract due date from text.
        
        Args:
            text: Text to extract from
            doc: spaCy document
            dates: List of extracted date entities
            
        Returns:
            Datetime object or None
        """
        # Look for explicit due date mentions
        due_patterns = [
            r'due\s+(?:by|on|before)?\s+([^\.,;]+)',
            r'deadline[:\s]+([^\.,;]+)',
            r'by\s+([^\.,;]+)'
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_text = match.group(1).strip()
                try:
                    return dateutil.parser.parse(date_text, fuzzy=True)
                except:
                    pass
        
        # Check for any dates in the text
        for date_text, _, _ in dates:
            try:
                return dateutil.parser.parse(date_text, fuzzy=True)
            except:
                pass
        
        # Look for relative dates
        tomorrow_pattern = r'\b(?:tomorrow|next day)\b'
        if re.search(tomorrow_pattern, text, re.IGNORECASE):
            return datetime.now() + timedelta(days=1)
        
        next_week_pattern = r'\bnext week\b'
        if re.search(next_week_pattern, text, re.IGNORECASE):
            return datetime.now() + timedelta(days=7)
        
        return None
    
    def _extract_priority(self, text):
        """
        Extract priority from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            Priority string or None
        """
        # Look for explicit priority mentions
        urgent_pattern = r'\b(?:urgent|asap|emergency|immediately|critical)\b'
        if re.search(urgent_pattern, text, re.IGNORECASE):
            return 'Urgent'
        
        high_pattern = r'\b(?:high priority|important|significant)\b'
        if re.search(high_pattern, text, re.IGNORECASE):
            return 'High'
        
        low_pattern = r'\b(?:low priority|when you have time|not urgent|can wait)\b'
        if re.search(low_pattern, text, re.IGNORECASE):
            return 'Low'
        
        return 'Medium'  # Default priority
    
    def _extract_location(self, text, doc):
        """
        Extract location from text.
        
        Args:
            text: Text to extract from
            doc: spaCy document
            
        Returns:
            Location string or None
        """
        # Look for location entities
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:
                return ent.text
        
        # Look for location patterns
        location_patterns = [
            r'at\s+([^\.,;]+)',
            r'in\s+([^\.,;]+)',
            r'location[:\s]+([^\.,;]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None