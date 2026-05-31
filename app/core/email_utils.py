import smtplib
import asyncio
from email.mime.text import MIMEText
from postmarker.core import PostmarkClient
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


async def send_email_postmark_async(to_email: str, subject: str, body: str):
    client = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
    def _send():
        client.emails.send(
            From=settings.POSTMARK_FROM_EMAIL,
            To=to_email,
            Subject=subject,
            TextBody=body
        )
    await asyncio.to_thread(_send)
    
def send_email_postmark_sync(to_email: str, subject: str, body: str):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        asyncio.ensure_future(send_email_postmark_async(to_email, subject, body))
    asyncio.run(send_email_postmark_async(to_email, subject, body))
