from django.conf import settings
from .resend_service import ResendEmailService

def get_email_service():
    service_name = getattr(settings, 'EMAIL_SERVICE', 'resend').lower()
    
    if service_name == 'resend':
        return ResendEmailService()
    else:
        raise ValueError(f"Serviço de e-mail {service_name} não configurado.")