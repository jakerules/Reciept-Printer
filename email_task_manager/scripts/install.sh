#!/bin/bash
# Installation script for Email Task Manager

# Print colored messages
print_green() {
    echo -e "\e[32m$1\e[0m"
}

print_yellow() {
    echo -e "\e[33m$1\e[0m"
}

print_red() {
    echo -e "\e[31m$1\e[0m"
}

# Check Python version
check_python() {
    print_yellow "Checking Python version..."
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_green "Found Python $python_version"
        
        # Check if version is at least 3.7
        if [[ $(echo "$python_version" | cut -d. -f1) -ge 3 && $(echo "$python_version" | cut -d. -f2) -ge 7 ]]; then
            print_green "Python version is compatible"
            return 0
        else
            print_red "Python version must be 3.7 or higher"
            return 1
        fi
    else
        print_red "Python 3 not found. Please install Python 3.7 or higher"
        return 1
    fi
}

# Create virtual environment
create_venv() {
    print_yellow "Creating virtual environment..."
    if python3 -m venv venv; then
        print_green "Virtual environment created successfully"
        return 0
    else
        print_red "Failed to create virtual environment"
        return 1
    fi
}

# Activate virtual environment
activate_venv() {
    print_yellow "Activating virtual environment..."
    source venv/bin/activate
    if [ $? -eq 0 ]; then
        print_green "Virtual environment activated"
        return 0
    else
        print_red "Failed to activate virtual environment"
        return 1
    fi
}

# Install dependencies
install_dependencies() {
    print_yellow "Installing dependencies..."
    if pip install -r requirements.txt; then
        print_green "Dependencies installed successfully"
        return 0
    else
        print_red "Failed to install dependencies"
        return 1
    fi
}

# Initialize database
init_database() {
    print_yellow "Initializing database..."
    if [ ! -d "migrations" ]; then
        flask db init
    fi
    flask db migrate -m "Initial migration"
    if flask db upgrade; then
        print_green "Database initialized successfully"
        return 0
    else
        print_red "Failed to initialize database"
        return 1
    fi
}

# Check for Gmail API credentials
check_credentials() {
    print_yellow "Checking for Gmail API credentials..."
    if [ -f "credentials.json" ]; then
        print_green "Found credentials.json file"
    else
        print_yellow "credentials.json file not found"
        print_yellow "You will need to obtain Gmail API credentials from Google Cloud Console"
        print_yellow "See README.md for instructions"
    fi
}

# Main installation process
main() {
    print_green "=== Email Task Manager Installation ==="
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ]; then
        print_red "Error: requirements.txt not found"
        print_red "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check Python version
    check_python || exit 1
    
    # Create and activate virtual environment
    create_venv || exit 1
    activate_venv || exit 1
    
    # Install dependencies
    install_dependencies || exit 1
    
    # Set environment variables
    export FLASK_APP=run.py
    
    # Initialize database
    init_database || exit 1
    
    # Check for Gmail API credentials
    check_credentials
    
    print_green "=== Installation Complete ==="
    print_green "To start the application, run:"
    print_yellow "source venv/bin/activate  # If not already activated"
    print_yellow "python run.py"
    print_green "Then access the application at http://localhost:5000"
}

# Run the main function
main