# Email Task Manager - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Database Schema](#database-schema)
4. [API Reference](#api-reference)
5. [Email Processing](#email-processing)
6. [Printing System](#printing-system)
7. [Development Guide](#development-guide)
8. [Deployment](#deployment)

## Architecture Overview

Email Task Manager is built using a Flask-based web application architecture with a SQLAlchemy ORM for database operations. The application follows a Model-View-Controller (MVC) pattern and is designed to be modular and extensible.

### Technology Stack

- **Backend Framework**: Flask 2.3.x
- **Database ORM**: SQLAlchemy 2.0.x
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Email Integration**: Gmail API
- **NLP Processing**: spaCy with optional OpenAI integration
- **Printing**: CUPS (Mac/Linux) and Windows Printing API

### Directory Structure

```
email_task_manager/
├── app/                    # Application package
│   ├── controllers/        # Route handlers and business logic
│   ├── models/             # Database models
│   ├── services/           # Service modules (email, printer, etc.)
│   ├── static/             # Static assets (CSS, JS, images)
│   └── templates/          # HTML templates
├── config/                 # Configuration files
├── docs/                   # Documentation
│   ├── technical/          # Technical documentation
│   └── user/               # User documentation
├── scripts/                # Utility scripts
└── tests/                  # Test suite
```

## System Components

### 1. Email Integration Service

The Email Integration Service handles the connection to Gmail, fetching emails, and parsing them into tasks.

**Key Components:**
- `GmailService`: Connects to Gmail API and fetches emails
- `EmailParser`: Parses email content to extract tasks

**Key Files:**
- `app/services/email/gmail_service.py`
- `app/services/email/email_parser.py`

### 2. Task Management System

The Task Management System handles the creation, updating, and management of tasks.

**Key Components:**
- `Task` model: Represents a task in the system
- `TaskController`: Handles task-related routes and operations

**Key Files:**
- `app/models/task.py`
- `app/controllers/tasks.py`

### 3. Receipt Printing Service

The Receipt Printing Service handles the formatting and printing of tasks as receipts.

**Key Components:**
- `PrinterService`: Handles printing operations
- `PrinterConfig` model: Stores printer configurations

**Key Files:**
- `app/services/printer/printer_service.py`
- `app/models/printer_config.py`

### 4. Database

The application uses SQLAlchemy ORM with SQLite as the default database, with options for PostgreSQL in production.

**Key Models:**
- `User`: User accounts and authentication
- `Email`: Stored emails fetched from Gmail
- `Task`: Tasks extracted from emails or created manually
- `PrinterConfig`: Printer configurations

**Key Files:**
- `app/models/*.py`

### 5. Web Interface

The web interface is built using Flask templates with Bootstrap 5 for styling.

**Key Components:**
- Templates for each section of the application
- JavaScript for dynamic interactions
- CSS for styling

**Key Files:**
- `app/templates/*.html`
- `app/static/js/main.js`
- `app/static/css/style.css`

## Database Schema

### User Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | String | Unique username |
| email | String | User's email address |
| password_hash | String | Hashed password |
| is_admin | Boolean | Administrator flag |
| created_at | DateTime | Account creation timestamp |
| last_login | DateTime | Last login timestamp |

### Email Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| gmail_id | String | Gmail message ID |
| sender | String | Sender name |
| sender_email | String | Sender email address |
| subject | String | Email subject |
| body_text | Text | Plain text body |
| body_html | Text | HTML body (if available) |
| received_at | DateTime | When email was received |
| processed_at | DateTime | When email was processed |
| is_processed | Boolean | Processing status flag |
| processing_error | Text | Error message (if any) |
| created_at | DateTime | Record creation timestamp |

### Task Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String | Task title |
| description | Text | Task description |
| priority | String | Priority level |
| status | String | Current status |
| due_date | DateTime | Due date (if any) |
| completed_at | DateTime | Completion timestamp |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| email_id | Integer | Foreign key to Email |
| assigned_to_id | Integer | Foreign key to User |
| requestor_name | String | Name of requestor |
| requestor_email | String | Email of requestor |
| requestor_phone | String | Phone of requestor |
| location | String | Task location |
| tags | String | Comma-separated tags |
| is_printed | Boolean | Printing status flag |
| last_printed_at | DateTime | Last print timestamp |
| print_count | Integer | Number of times printed |

### PrinterConfig Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Configuration name |
| description | String | Description |
| printer_type | String | Type of printer |
| printer_name | String | System printer name |
| printer_address | String | IP address or USB ID |
| printer_port | Integer | Port number |
| paper_width | Integer | Characters per line |
| header_text | Text | Receipt header text |
| footer_text | Text | Receipt footer text |
| font_size | String | Font size |
| include_logo | Boolean | Logo inclusion flag |
| logo_path | String | Path to logo file |
| auto_print | Boolean | Auto-print flag |
| print_on_status_change | Boolean | Print on status change flag |
| cut_paper | Boolean | Paper cutting flag |
| copies | Integer | Number of copies |
| is_default | Boolean | Default printer flag |
| is_active | Boolean | Active status flag |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## API Reference

The application provides several internal APIs for interacting with the system programmatically.

### Authentication API

- `POST /api/auth/login`: Authenticate a user
- `POST /api/auth/logout`: Log out the current user
- `GET /api/auth/user`: Get current user information

### Tasks API

- `GET /api/tasks`: Get all tasks
- `GET /api/tasks/<id>`: Get a specific task
- `POST /api/tasks`: Create a new task
- `PUT /api/tasks/<id>`: Update a task
- `DELETE /api/tasks/<id>`: Delete a task
- `POST /api/tasks/<id>/status`: Update task status
- `POST /api/tasks/<id>/assign`: Assign a task to a user
- `POST /api/tasks/<id>/print`: Print a task

### Emails API

- `GET /api/emails`: Get all emails
- `GET /api/emails/<id>`: Get a specific email
- `POST /api/emails/fetch`: Fetch new emails
- `POST /api/emails/<id>/process`: Process an email
- `DELETE /api/emails/<id>`: Delete an email

### Printer API

- `GET /api/printers`: Get all printer configurations
- `GET /api/printers/<id>`: Get a specific printer configuration
- `POST /api/printers`: Create a new printer configuration
- `PUT /api/printers/<id>`: Update a printer configuration
- `DELETE /api/printers/<id>`: Delete a printer configuration
- `POST /api/printers/<id>/test`: Test a printer
- `POST /api/printers/<id>/default`: Set as default printer
- `POST /api/print`: Print tasks

## Email Processing

### Gmail Integration

The application uses the Gmail API to fetch emails. The process works as follows:

1. User authenticates with Gmail using OAuth 2.0
2. Application requests access to read emails
3. Application periodically checks for new unread emails
4. New emails are downloaded and stored in the database
5. Emails are marked as read in Gmail

### Email Parsing

The application uses two methods for parsing emails:

1. **Rule-based parsing** (default):
   - Uses spaCy for NLP processing
   - Looks for bullet points and numbered lists
   - Identifies sentences with action verbs
   - Extracts dates, times, and locations
   - Determines priority based on keywords

2. **OpenAI-based parsing** (optional):
   - Uses OpenAI's language models for more accurate parsing
   - Sends the email content to OpenAI API
   - Extracts structured task information
   - Handles complex and unstructured emails better

### Task Extraction Logic

The task extraction process follows these steps:

1. Identify potential task candidates in the email
2. Extract relevant information for each task:
   - Title and description
   - Due date (if mentioned)
   - Priority (based on urgency keywords)
   - Location (if mentioned)
3. Create task records in the database
4. Associate tasks with the source email

## Printing System

### Printer Types

The application supports multiple printer types:

1. **CUPS Printer**: For Mac and Linux systems
   - Uses the CUPS printing system
   - Requires the printer to be configured in the OS

2. **Windows Printer**: For Windows systems
   - Uses the Windows printing API
   - Requires the printer to be installed in Windows

3. **Network Printer**: For network-connected receipt printers
   - Connects directly to the printer via IP
   - Uses ESC/POS commands

4. **USB Printer**: For directly connected USB receipt printers
   - Connects directly to the printer via USB
   - Uses ESC/POS commands

5. **File Output**: For testing
   - Outputs to a text file
   - Useful for debugging

### Receipt Formatting

The application formats tasks as receipts with the following structure:

```
===============================
         TASK RECEIPT
===============================
Task ID: 123
Created: 2023-01-01 12:00

TITLE: Example Task Title

DESCRIPTION:
This is an example task description
that might span multiple lines
depending on the paper width.

Priority: High
Status: New
Due: 2023-01-15 17:00

From: John Doe
Email: john@example.com
Location: Conference Room A
===============================
      Printed: 2023-01-01 12:30
```

The formatting is customizable through the printer configuration:
- Paper width (characters per line)
- Header and footer text
- Font size
- Logo inclusion

### Printing Process

The printing process works as follows:

1. User selects a task or tasks to print
2. Application formats the task(s) as receipts
3. Application sends the formatted text to the printer:
   - For CUPS/Windows: Creates a temporary file and prints it
   - For Network/USB: Sends ESC/POS commands directly
4. Application updates the task's printing status
5. Application logs the printing operation

## Development Guide

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```
   export FLASK_APP=run.py
   export FLASK_DEBUG=1
   ```
5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. Run the development server:
   ```
   flask run
   ```

### Adding New Features

#### Adding a New Model

1. Create a new file in `app/models/`
2. Define your model class extending `db.Model`
3. Import the model in `app/models/__init__.py`
4. Create a database migration:
   ```
   flask db migrate -m "Add new model"
   flask db upgrade
   ```

#### Adding a New Controller

1. Create a new file in `app/controllers/`
2. Define your routes using Flask's Blueprint
3. Import and register the blueprint in `app/__init__.py`

#### Adding a New Service

1. Create a new file in `app/services/`
2. Define your service class or functions
3. Import the service where needed

### Testing

The application includes a test suite using pytest:

```
pytest
```

To run specific tests:

```
pytest tests/test_email_parser.py
```

To generate a coverage report:

```
pytest --cov=app tests/
```

## Deployment

### Production Configuration

For production deployment, update the configuration:

1. Set `FLASK_ENV=production`
2. Set a strong `SECRET_KEY`
3. Configure a production database (PostgreSQL recommended)
4. Set up proper logging
5. Configure HTTPS

### Deployment Options

#### Option 1: Traditional Server

1. Set up a server with Python installed
2. Clone the repository
3. Install dependencies
4. Set up a production WSGI server (Gunicorn, uWSGI)
5. Configure a reverse proxy (Nginx, Apache)

Example Gunicorn configuration:
```
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

Example Nginx configuration:
```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Option 2: Docker Deployment

1. Build the Docker image:
   ```
   docker build -t email-task-manager .
   ```
2. Run the container:
   ```
   docker run -p 80:5000 -e SECRET_KEY=your_secret_key email-task-manager
   ```

#### Option 3: Cloud Deployment

The application can be deployed to various cloud platforms:

- **Heroku**:
  - Create a `Procfile`
  - Push to Heroku
  - Configure environment variables

- **AWS Elastic Beanstalk**:
  - Create an application
  - Upload the code
  - Configure environment

- **Google Cloud Run**:
  - Build a container
  - Push to Google Container Registry
  - Deploy to Cloud Run

### Database Migration in Production

To update the database schema in production:

1. Generate migration:
   ```
   flask db migrate -m "Description of changes"
   ```
2. Review the generated migration script
3. Apply the migration:
   ```
   flask db upgrade
   ```

### Backup and Recovery

Regular backups are recommended:

1. Database backup:
   ```
   # SQLite
   cp instance/app.db backup/app.db.$(date +%Y%m%d)
   
   # PostgreSQL
   pg_dump -U username -d database_name > backup/db.$(date +%Y%m%d).sql
   ```

2. Configuration backup:
   ```
   cp config/config.py backup/config.py.$(date +%Y%m%d)
   ```

3. Gmail API credentials backup:
   ```
   cp credentials.json backup/credentials.json.$(date +%Y%m%d)
   cp token.json backup/token.json.$(date +%Y%m%d)
   ```

To restore from backup:

1. Stop the application
2. Restore the database and configuration files
3. Restart the application