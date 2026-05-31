from app.celery_app import celery_app
from app.core.email_utils import send_email_postmark_sync

                                                                                                                                            
    
@celery_app.task(name="app.tasks.email_tasks.send_verification_email_task")
def send_verification_email_task(to_email: str, full_name: str, code: str):
    subject = "Please Verify Your Email"
    body = (
        f"Hello {full_name.title()},\n\n"
        f"This your email verification code: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Regards,\nYour App Team"  # Fix: removed stray 'x'
    )
    send_email_postmark_sync(to_email, subject, body)

@celery_app.task(name="app.tasks.email_tasks.send_password_reset_email_task")
def send_password_reset_email_task(to_email: str, full_name: str, code: str):
    subject = "Your Password Reset Code"
    body = (
        f"Hello {full_name.title()},\n\n"
        f"Your password reset code is: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Regards,\nYour App Team"
    )
    send_email_postmark_sync(to_email, subject, body)