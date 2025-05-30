#!/usr/bin/env python3
"""
Bislett monitor for GitHub Actions
Uses environment variables for email configuration
"""

import requests
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
URL_TO_CHECK = "https://www.romerikeultra.no/next/p/24684/bislett-24-timers"
SEARCH_PHRASE = "Det er i øyeblikket ingen plasser til salgs"

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_email_alert(subject, body):
    """Send email alert using environment variables"""
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        log_message("Email configuration missing in environment variables")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        log_message("Email alert sent successfully!")
        return True
        
    except Exception as e:
        log_message(f"Failed to send email: {str(e)}")
        return False

def check_website():
    """Check if the phrase is still on the website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'no,nb;q=0.9,en;q=0.8'
        }
        
        # Use requests with SSL verification disabled
        response = requests.get(URL_TO_CHECK, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        
        content = response.text
        phrase_found = SEARCH_PHRASE in content
        
        if phrase_found:
            log_message(f"✓ Phrase found - registration still closed")
            return True, "closed"
        else:
            log_message(f"⚠️ PHRASE NOT FOUND - REGISTRATION MIGHT BE OPEN!")
            return True, "open"
            
    except requests.exceptions.RequestException as e:
        log_message(f"Request error: {str(e)}")
        return False, "error"
    except Exception as e:
        log_message(f"Error checking website: {str(e)}")
        return False, "error"

def main():
    """Main monitoring function"""
    log_message("=== Bislett 24-hour Registration Monitor (GitHub Actions) ===")
    log_message(f"Monitoring URL: {URL_TO_CHECK}")
    log_message(f"Looking for phrase: '{SEARCH_PHRASE}'")
    
    success, status = check_website()
    
    if not success:
        log_message("Failed to check website")
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

This is an automated alert from your GitHub Actions monitor.
        """.strip()
        
        send_email_alert(subject, body)
    
    log_message("=== Check completed ===")

if __name__ == "__main__":
    main()