from app.celery_app import celery_app
from app.core.email_utils import send_email_postmark_sync
from app.core.config import settings
from app.core.logging_config import logger
                                                                                                                                            
    
@celery_app.task(name="app.tasks.email_tasks.send_verification_email_task", bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, to_email: str, full_name: str, code: str):
    subject = "Please Verify Your Email"
    body = (
        f"Hello {full_name.title()},\n\n"
        f"This your email verification code: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Regards,\nYour App Team"  # Fix: removed stray 'x'
    )
    # Switch between real email and console logging
    if not settings.SEND_EMAILS:
        logger.info(
            "SIMULATION MODE - Verification Email Details:\n"
            f"  -> To: {to_email}\n"
            f"  -> Code: {code}\n"
            f"  -> Subject: {subject}\n"
            f"  -> Body Summary: {body.replace('\n', ' ')}"
        )
        return "Verification email logged successfully"
    try:
        send_email_postmark_sync(to_email, subject, body)
    except Exception as exc:
        raise self.retry(exc=exc)

@celery_app.task(name="app.tasks.email_tasks.send_password_reset_email_task", bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, to_email: str, full_name: str, code: str):
    subject = "Your Password Reset Code"
    body = (
        f"Hello {full_name.title()},\n\n"
        f"Your password reset code is: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Regards,\nYour App Team"
    )
    if not settings.SEND_EMAILS:
        logger.info(
            "SIMULATION MODE - Reset Password Details:\n"
            f"  -> To: {to_email}\n"
            f"  -> Code: {code}\n"
            f"  -> Subject: {subject}\n"
            f"  -> Body Summary: {body.replace('\n', ' ')}"
        )
        return "logged"
    try:
        send_email_postmark_sync(to_email, subject, body)
    except Exception as exc:
        raise self.retry(exc=exc)