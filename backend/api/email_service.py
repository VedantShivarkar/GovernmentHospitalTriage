import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_SENDER")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_triage_email(patient_email: str, priority: int, department: str, wait_time: float, summary: str) -> bool:
    """
    Sends a secure SMTP email to the patient with their AI-calculated wait time and department.
    """
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("Warning: Email credentials missing. Skipping notification.")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = patient_email
    msg['Subject'] = "Govt Hospital AI Triage - Your Appointment Status"

    # Dynamic urgency formatting
    urgency_label = "CRITICAL / IMMEDIATE" if priority <= 2 else "Standard Queue"
    
    body = f"""
    Hello,

    Your symptom report has been processed by the Hospital AI Triage System.

    Triage Summary: {summary}
    Assigned Department: {department}
    Priority Level: {priority} ({urgency_label})
    
    Estimated Wait Time: {wait_time} minutes.

    Please proceed directly to the {department} waiting area. 
    If your symptoms worsen, notify the emergency desk immediately.

    - Automated Triage & Scheduling Infrastructure
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Standard Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Success: Notification email sent to {patient_email}")
        return True
    except Exception as e:
        print(f"SMTP Error: Failed to send email to {patient_email}. Details: {str(e)}")
        return False