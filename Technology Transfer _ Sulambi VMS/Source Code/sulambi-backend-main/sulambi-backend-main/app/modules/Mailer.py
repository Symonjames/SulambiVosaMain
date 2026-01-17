from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from threading import Thread
import os

load_dotenv()

EMAIL = os.getenv("AUTOMAILER_EMAIL")
PASSW = os.getenv("AUTOMAILER_PASSW")

def isEmailConfigured():
  """Check if email configuration is properly set up"""
  return EMAIL is not None and PASSW is not None and EMAIL != "" and PASSW != ""

def validateEmailConfig():
  """Validate email configuration and return status"""
  if not isEmailConfigured():
    return {
      "configured": False,
      "message": "Email configuration missing. Please set AUTOMAILER_EMAIL and AUTOMAILER_PASSW in .env file"
    }
  
  try:
    # Test SMTP connection with timeout
    import socket
    socket.setdefaulttimeout(10)  # 10 second timeout
    
    smtp = SMTP("smtp.gmail.com", 587)
    smtp.set_debuglevel(0)  # Disable debug output
    smtp.ehlo()
    smtp.starttls()
    smtp.login(EMAIL, PASSW)
    smtp.close()
    
    # Reset timeout
    socket.setdefaulttimeout(None)
    
    return {
      "configured": True,
      "message": "Email configuration is valid"
    }
  except socket.timeout:
    return {
      "configured": False,
      "message": "Email configuration test timed out. SMTP connection to smtp.gmail.com:587 timed out after 10 seconds."
    }
  except Exception as e:
    return {
      "configured": False,
      "message": f"Email configuration test failed: {str(e)}"
    }

def sendMail(mailTo: str, content):
  Smtp = SMTP("smtp.gmail.com", 587)
  Smtp.ehlo()
  Smtp.starttls()
  Smtp.login(EMAIL, PASSW)
  Smtp.sendmail(EMAIL, mailTo, content)
  Smtp.close()

def htmlMailer(mailTo: str, subject: str, htmlRendered: str):
  """Send HTML email with error handling"""
  if not isEmailConfigured():
    print(f"[EMAIL ERROR] Email not configured. Cannot send email to {mailTo}")
    return False
  
  try:
    messageMime = MIMEMultipart()
    messageMime["from"] = EMAIL
    messageMime["to"] = mailTo
    messageMime["subject"] = subject

    messageMime.attach(MIMEText(htmlRendered, "html"))
    Smtp = SMTP("smtp.gmail.com", 587)
    Smtp.ehlo()
    Smtp.starttls()
    Smtp.login(EMAIL, PASSW)
    Smtp.sendmail(EMAIL, mailTo, messageMime.as_string())
    Smtp.close()
    print(f"[EMAIL SUCCESS] Email sent to {mailTo}")
    return True
  except Exception as e:
    print(f"[EMAIL ERROR] Failed to send email to {mailTo}: {str(e)}")
    return False

def threadedHtmlMailer(mailTo: str, subject: str, htmlRendered: str):
  """Send HTML email in background thread with error handling"""
  th = Thread(target=htmlMailer, args=(mailTo, subject, htmlRendered))
  th.daemon = True
  th.start()
