# Email Task Manager - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Email Integration](#email-integration)
4. [Task Management](#task-management)
5. [Receipt Printing](#receipt-printing)
6. [Settings and Configuration](#settings-and-configuration)
7. [Troubleshooting](#troubleshooting)

## Introduction

Email Task Manager is a comprehensive application designed to streamline the process of converting emails into actionable tasks and printing them as receipts. This application is ideal for businesses and individuals who need to track and manage tasks that come in via email.

### Key Features

- **Email Integration**: Connect to Gmail to automatically fetch and parse emails
- **Task Extraction**: Extract tasks from email content using NLP or AI
- **Task Management**: Organize, prioritize, and track tasks
- **Receipt Printing**: Print tasks as receipts on thermal printers
- **Cross-Platform**: Works on both Mac and Windows operating systems

## Getting Started

### System Requirements

- Operating System: Windows, macOS, or Linux
- Python 3.7 or higher
- Internet connection for email fetching
- Receipt printer (optional, for printing tasks)

### Installation

1. Clone or download the Email Task Manager application
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Gmail API credentials (see [Email Integration](#email-integration))
4. Run the application:
   ```
   python run.py
   ```
5. Access the application in your web browser at `http://localhost:5000`

### First-Time Setup

1. **Create an Account**: Register a new user account on the login page
   - The first user created will automatically be an administrator
   - Additional users can be registered later

2. **Configure Email Integration**: Set up your Gmail API credentials
   - Follow the instructions in the [Email Integration](#email-integration) section

3. **Configure Printer**: Set up your receipt printer
   - Follow the instructions in the [Receipt Printing](#receipt-printing) section

## Email Integration

### Setting Up Gmail API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API for your project
4. Create OAuth 2.0 credentials
   - Application type: Desktop application
   - Download the credentials.json file
5. In the Email Task Manager application:
   - Go to Settings
   - Upload the credentials.json file
   - Click "Authorize" to grant access to your Gmail account

### Email Fetching

The application will automatically check for new emails based on the configured interval (default: 5 minutes). You can also manually check for new emails:

1. Go to the Dashboard or Emails page
2. Click the "Check Emails" button

### Email Processing

When new emails are fetched, they are initially marked as "Unprocessed". To process an email:

1. Go to the Emails page
2. Click on an unprocessed email to view it
3. Click the "Process Email" button

The application will analyze the email content and extract tasks based on:
- Bullet points or numbered lists
- Sentences containing action verbs
- Dates and deadlines mentioned
- Priority indicators

If OpenAI integration is enabled, the application will use AI to more accurately extract tasks from emails.

## Task Management

### Task List

The Tasks page displays all tasks in the system. You can:
- Filter tasks by status, priority, and assignment
- Search for specific tasks
- Sort tasks by different criteria
- Select multiple tasks for batch actions

### Task Details

Click on a task to view its details, including:
- Title and description
- Priority and status
- Due date
- Requestor information
- Source email (if created from an email)

### Creating Tasks

Tasks can be created in two ways:
1. **Automatically**: Through email processing
2. **Manually**: By clicking the "New Task" button

When creating a task manually, fill in the following information:
- Title (required)
- Description
- Priority (Low, Medium, High, Urgent)
- Status (New, In Progress, Completed, Cancelled)
- Due date
- Assignment (which user is responsible)
- Requestor information

### Managing Tasks

From the task details page, you can:
- Edit task information
- Update task status
- Assign the task to a user
- Print the task as a receipt
- Delete the task

## Receipt Printing

### Printer Configuration

To set up a printer:
1. Go to the Printer page
2. Click "Add Printer"
3. Fill in the printer details:
   - Name and description
   - Printer type (CUPS, Windows, Network, USB, File)
   - Printer name or address
   - Receipt formatting options
   - Behavior settings

### Printer Types

The application supports several printer types:
- **CUPS Printer**: For Mac and Linux systems using CUPS
- **Windows Printer**: For Windows systems using the Windows printing API
- **Network Printer**: For network-connected receipt printers (using IP address)
- **USB Printer**: For directly connected USB receipt printers
- **File Output**: For testing, outputs to a text file

### Receipt Formatting

You can customize the receipt format:
- Paper width (characters per line)
- Font size
- Header and footer text
- Logo inclusion (if supported by the printer)

### Printing Tasks

To print a task:
1. Go to the task details page
2. Click the "Print Task" button

To print multiple tasks:
1. Go to the Tasks page
2. Select the tasks you want to print
3. Click the "Print Selected" button
4. Choose a printer (or use the default)
5. Click "Print Tasks"

### Auto-Printing

You can configure the application to automatically print tasks:
- When new tasks are created
- When task status changes

To enable auto-printing:
1. Go to the Printer page
2. Edit your printer configuration
3. Enable the "Auto-print New Tasks" option

## Settings and Configuration

### Application Settings

The Settings page allows you to configure various aspects of the application:
- Email check interval
- Default task priority
- Auto-assignment of tasks

### Email Settings

Configure email integration settings:
- Gmail API credentials
- OpenAI integration for email parsing
- OpenAI API key (if using OpenAI)

### User Settings

Each user can configure their own preferences:
- Email notifications
- Auto-printing of assigned tasks

### System Information

The Settings page also displays system information:
- Operating system
- Python version
- Database type
- Environment (Development/Production)

## Troubleshooting

### Email Integration Issues

**Problem**: Cannot connect to Gmail
- Check that your credentials.json file is valid
- Ensure you've completed the OAuth authorization process
- Verify your internet connection

**Problem**: No emails are being fetched
- Check that the email check interval is not too long
- Verify that you have unread emails in your Gmail account
- Check the application logs for errors

### Printing Issues

**Problem**: Cannot print tasks
- Verify that your printer is properly connected and powered on
- Check that the printer configuration is correct
- Test the printer using the "Test Print" button
- Check the application logs for printing errors

**Problem**: Receipt formatting is incorrect
- Adjust the paper width setting to match your printer
- Check that the font size is appropriate
- Verify that the printer type is correct for your system

### General Issues

**Problem**: Application won't start
- Check that all dependencies are installed
- Verify that the database file is not corrupted
- Check the application logs for startup errors

**Problem**: Tasks are not being extracted from emails
- Check that the email content is properly formatted
- Consider enabling OpenAI integration for better extraction
- Try processing the email manually

For additional help, please contact support or refer to the technical documentation.