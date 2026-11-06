from app.celery_app import celery_app
from app.core.email_utils import send_email_resend_sync
from app.core.config import settings
from app.core.logging_config import logger
                                                                                                                                            
    
@celery_app.task(name="app.tasks.email_tasks.send_verification_email_task", bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, to_email: str, full_name: str, code: str):
    subject = "Please Verify Your Email"
    body = (
        f"Hello {full_name.title()},\n\n"
        f"Your email verification code is: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Regards,\nYour App Team"  # Fix: removed stray 'x'
    )
    # Switch between real email and console logging
    if not settings.SEND_EMAILS:
        logger.info(
            "SIMULATION MODE - Verification email generated for recipient %s",
            to_email
        )
        return "Verification email logged successfully"
    try:
        send_email_resend_sync(to_email, subject, body)
        logger.info("Verification email successfully submitted to Resend")
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
            "SIMULATION MODE - Password reset email generated for recipient %s",
            to_email
        )
        return "logged"
    try:
        send_email_resend_sync(to_email, subject, body)
        logger.info("Reset email successfully submitted to Resend")
    except Exception as exc:
        raise self.retry(exc=exc)