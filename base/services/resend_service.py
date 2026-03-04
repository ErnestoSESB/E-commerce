import resend
from django.conf import settings
from .email_service import EmailService

class ResendEmailService(EmailService):
    def __init__(self):
        resend.api_key = getattr(settings, 'RESEND_API_KEY', '')

    def send_email(self, to: str, subject: str, body: str) -> bool:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nexum.com')
        try:
            resend.Emails.send({
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": body,  
            })
            return True
        except Exception as e:
            print(f"Erro ao enviar email com Resend: {e}")
            return False