import smtplib
import asyncio
import resend
from email.mime.text import MIMEText
from app.core.config import settings

async def send_email_365_async(
    to_email: str,
    subject: str,
    body: str
):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.M365_EMAIL
    msg["To"] = to_email

    def _send():
        with smtplib.SMTP(settings.M365_SMTP_HOST, settings.M365_SMTP_PORT) as server:
            server.starttls()
            server.login(settings.M365_EMAIL, settings.M365_APP_PASSWORD)
            server.sendmail(settings.M365_EMAIL, [to_email], msg.as_string())
    await asyncio.to_thread(_send)


def send_email_resend_sync(
    to_email: str,
    subject: str,
    body: str
):
    resend.api_key = settings.RESEND_API_KEY

    params = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }

    return resend.Emails.send(params)