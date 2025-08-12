# Email Task Manager

A comprehensive application for parsing emails, managing tasks, and printing receipts.

## Overview

Email Task Manager is a web-based application that integrates email parsing, task management, and receipt printing capabilities. The application can receive emails, extract relevant information, create tasks based on email content, and print these tasks as receipts.

![Dashboard Screenshot](docs/images/dashboard.png)

## Features

- **Email Integration**: Connect to Gmail to automatically fetch and parse emails
- **Task Extraction**: Extract tasks from email content using NLP or AI
- **Task Management**: Create, edit, assign, and track tasks
- **Receipt Printing**: Print tasks as receipts on thermal printers
- **Cross-Platform**: Works on both Mac and Windows operating systems
- **User Management**: Multiple user accounts with authentication
- **Customizable**: Configure email checking frequency, printer settings, and more

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **Database**: SQLite (default) or PostgreSQL
- **Printer**: Any receipt printer compatible with your OS (optional)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/email-task-manager.git
   cd email-task-manager
   ```

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
   # Linux/Mac
   export FLASK_APP=run.py
   export FLASK_DEBUG=1  # For development only
   
   # Windows
   set FLASK_APP=run.py
   set FLASK_DEBUG=1  # For development only
   ```

5. Run the application:
   ```
   python run.py
   ```

6. Access the application in your web browser at `http://localhost:5000`

## Gmail API Setup

To use the email integration features, you need to set up Gmail API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API for your project
4. Create OAuth 2.0 credentials
   - Application type: Desktop application
   - Download the credentials.json file
5. Place the credentials.json file in the application root directory
6. The first time you run the application, it will prompt you to authorize access to your Gmail account

## Printer Setup

The application supports various printer types:

- **CUPS Printer**: For Mac and Linux systems
- **Windows Printer**: For Windows systems
- **Network Printer**: For network-connected receipt printers
- **USB Printer**: For directly connected USB receipt printers
- **File Output**: For testing, outputs to a text file

To configure a printer:
1. Log in to the application
2. Go to the Printer page
3. Click "Add Printer"
4. Fill in the printer details

## Documentation

For more detailed information, please refer to the documentation:

- [User Guide](docs/user/user_guide.md): Instructions for using the application
- [Technical Documentation](docs/technical/technical_documentation.md): Technical details for developers

## Development

### Project Structure

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
├── scripts/                # Utility scripts
└── tests/                  # Test suite
```

### Running Tests

```
pytest
```

### Creating Database Migrations

```
flask db migrate -m "Description of changes"
flask db upgrade
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask and its extensions
- SQLAlchemy ORM
- Bootstrap for UI components
- spaCy for NLP processing
- Gmail API for email integration