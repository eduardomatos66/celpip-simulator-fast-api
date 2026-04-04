from app.core.logger import logger

def send_approval_email(email: str, full_name: str):
    """
    Mock email sender for account approval.
    """
    logger.info(f"📧 EMAIL: Sending approval email to {email}")
    # In production, integrate with SendGrid, Resend, or AWS SES
    print(f"To: {email}\nSubject: CELPIP Simulator — Account Approved\nBody: Hello {full_name}, your account has been approved. You can now access the simulator.")

def send_rejection_email(email: str, full_name: str):
    """
    Mock email sender for account rejection.
    """
    logger.info(f"📧 EMAIL: Sending rejection email to {email}")
    print(f"To: {email}\nSubject: CELPIP Simulator — Access Request Denied\nBody: Hello {full_name}, unfortunately your access request was denied.")

def send_pending_email(email: str, full_name: str):
    """
    Mock email sender for pending approval registration.
    """
    logger.info(f"📧 EMAIL: Sending pending review email to {email}")
    print(f"To: {email}\nSubject: CELPIP Simulator — Account Under Review\nBody: Hello {full_name}, your account is currently under review by our admins.")

def send_revocation_email(email: str, full_name: str):
    """
    Mock email sender for account revocation.
    """
    logger.info(f"📧 EMAIL: Sending revocation email to {email}")
    print(f"To: {email}\nSubject: CELPIP Simulator — Access Revoked\nBody: Hello {full_name}, your access to the CELPIP simulator has been revoked by an administrator.")
