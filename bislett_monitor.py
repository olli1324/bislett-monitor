#!/usr/bin/env python3
"""
Bislett 24-hour registration monitor
Checks if registration is open by looking for the "no spots available" message
"""

import urllib.request
import urllib.error
import ssl
import smtplib
import time
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
URL_TO_CHECK = "https://www.romerikeultra.no/next/p/24684/bislett-24-timers"
SEARCH_PHRASE = "Det er i øyeblikket ingen plasser til salgs"
LOG_FILE = "bislett_monitor.log"
CONFIG_FILE = "email_config.json"

# Email configuration template (create email_config.json with your details)
EMAIL_CONFIG_TEMPLATE = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "your_email@gmail.com"
}

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def load_email_config():
    """Load email configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        log_message(f"Creating email config template: {CONFIG_FILE}")
        with open(CONFIG_FILE, "w") as f:
            json.dump(EMAIL_CONFIG_TEMPLATE, f, indent=2)
        log_message("Please edit email_config.json with your email settings")
        return None
    
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def send_email_alert(subject, body):
    """Send email alert"""
    config = load_email_config()
    if not config:
        log_message("Email configuration not found - cannot send alert")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = config['recipient_email']
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()  # Enable security
        server.login(config['sender_email'], config['sender_password'])
        
        # Send email
        text = msg.as_string()
        server.sendmail(config['sender_email'], config['recipient_email'], text)
        server.quit()
        
        log_message("Email alert sent successfully!")
        return True
        
    except Exception as e:
        log_message(f"Failed to send email: {str(e)}")
        return False

def check_website():
    """Check if the phrase is still on the website"""
    try:
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create request with browser headers
        req = urllib.request.Request(URL_TO_CHECK)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        req.add_header('Accept-Language', 'no,nb;q=0.9,en;q=0.8')
        
        # Fetch the page
        response = urllib.request.urlopen(req, context=ssl_context, timeout=30)
        content = response.read().decode('utf-8', errors='ignore')
        response.close()
        
        # Check if the phrase is found
        phrase_found = SEARCH_PHRASE in content
        
        if phrase_found:
            log_message(f"✓ Phrase found - registration still closed")
            return True, "closed"
        else:
            log_message(f"⚠️ PHRASE NOT FOUND - REGISTRATION MIGHT BE OPEN!")
            return True, "open"
            
    except urllib.error.HTTPError as e:
        log_message(f"HTTP Error {e.code}: {e.reason}")
        return False, "error"
    except urllib.error.URLError as e:
        log_message(f"URL Error: {e.reason}")
        return False, "error"
    except Exception as e:
        log_message(f"Error checking website: {str(e)}")
        return False, "error"

def main():
    """Main monitoring function"""
    log_message("=== Bislett 24-hour Registration Monitor Started ===")
    log_message(f"Monitoring URL: {URL_TO_CHECK}")
    log_message(f"Looking for phrase: '{SEARCH_PHRASE}'")
    
    success, status = check_website()
    
    if not success:
        log_message("Failed to check website - will try again next time")
        return
    
    if status == "open":
        # Registration might be open - send alert!
        subject = "🏃‍♂️ BISLETT 24-HOUR REGISTRATION ALERT!"
        body = f"""
IMPORTANT: The registration monitoring phrase was not found on the Bislett 24-hour page!

This might mean that registration is now OPEN.

Please check immediately: {URL_TO_CHECK}

Monitoring phrase: "{SEARCH_PHRASE}"
Time checked: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This is an automated alert from your Bislett monitor script.
        """.strip()
        
        send_email_alert(subject, body)
        
        # Also create a desktop notification if possible
        try:
            import subprocess
            subprocess.run([
                'osascript', '-e', 
                f'display notification "Registration might be open!" with title "Bislett 24-hour Alert"'
            ])
        except:
            pass  # Desktop notification failed, but email should work
    
    log_message("=== Check completed ===\n")

if __name__ == "__main__":
    main()