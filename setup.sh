#!/bin/bash
# Setup script for Bislett monitor

echo "Setting up Bislett 24-hour registration monitor..."

# Install required Python package
echo "Installing required packages..."
pip3 install schedule

# Create the Python files
echo "Python scripts should be saved as:"
echo "  - bislett_monitor.py (main monitoring script)"
echo "  - scheduler.py (scheduler script)"

# Make scripts executable
chmod +x bislett_monitor.py
chmod +x scheduler.py

echo ""
echo "Setup complete!"
echo ""
echo "NEXT STEPS:"
echo "1. Edit email_config.json with your email settings (will be created on first run)"
echo "2. If using Gmail, you'll need an 'App Password' instead of your regular password"
echo "3. Run the monitor: python3 scheduler.py"
echo ""
echo "The monitor will:"
echo "  - Check the website 10 times per day"
echo "  - Send email alerts when registration opens"
echo "  - Log all activity to bislett_monitor.log"
echo ""
echo "For Gmail setup:"
echo "  1. Enable 2-factor authentication"
echo "  2. Generate an App Password: https://myaccount.google.com/apppasswords"
echo "  3. Use the App Password in email_config.json"