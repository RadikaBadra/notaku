import smtplib
from email.message import EmailMessage
import os

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_verification_email(to_email: str, link: str):
    msg = EmailMessage()
    msg["Subject"] = "Verify your account"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(
        f"""
        Welcome!

        Please verify your account by clicking the link below:
        {link}

        This link will expire in 30 minutes.
        """
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

def send_password_reset_email(to_email: str, link: str):
    msg = EmailMessage()
    msg["Subject"] = "Reset your password"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(
        f"""
        You requested a password reset.

        Please reset your password by clicking the link below:
        {link}

        This link will expire in 30 minutes.
        """
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)