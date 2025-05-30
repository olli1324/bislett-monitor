#!/usr/bin/env python3
"""
Simple email test script to verify email configuration works
"""

import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    """Send a test email to verify configuration"""
    
    # Load email config
    try:
        with open("email_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ email_config.json not found!")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in email_config.json")
        return False
    
    print(f"📧 Sending test email from {config['sender_email']} to {config['recipient_email']}")
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = config['recipient_email']
        msg['Subject'] = "🧪 Bislett Monitor Test Email"
        
        body = f"""
This is a TEST email from your Bislett monitoring system.

✅ Email configuration is working correctly!
✅ SMTP connection successful
✅ Authentication successful

Test sent at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

If you receive this email, your monitoring system is ready to send alerts when Bislett registration opens.

---
Bislett Monitor Test System
        """.strip()
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP
        print("🔐 Connecting to Gmail SMTP...")
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        
        print("🔑 Authenticating...")
        server.login(config['sender_email'], config['sender_password'])
        
        print("📤 Sending email...")
        text = msg.as_string()
        server.sendmail(config['sender_email'], config['recipient_email'], text)
        server.quit()
        
        print("✅ TEST EMAIL SENT SUCCESSFULLY!")
        print(f"📬 Check your inbox at {config['recipient_email']}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed!")
        print("   Check your email and app password in email_config.json")
        print("   Make sure you're using a Gmail App Password, not your regular password")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Bislett Monitor Email Test ===")
    print()
    
    success = send_test_email()
    
    print()
    if success:
        print("🎉 Email test completed successfully!")
        print("Your Bislett monitor is ready to send alerts.")
    else:
        print("💥 Email test failed!")
        print("Please check your email_config.json settings.")
    
    print("=== Test Complete ===")