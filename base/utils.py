from rest_framework import serializers
import nh3
import uuid
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from base.services.email_factory import get_email_service

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user):
    otp = generate_otp()
    user.security_profile.otp_code = otp
    user.security_profile.otp_created_at = timezone.now()
    user.security_profile.save()
    subject = 'Seu código de verificação (2FA)'
    message = f'Olá {user.name},\n\nSeu código de verificação é: {otp}\n\nEste código expira em 10 minutos.'
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@nexum.com'
    send_mail(subject, message, from_email, [user.email], fail_silently=False)

def send_password_reset_email(user):
    # O token de recuperação de senha é gerado usando uuid.uuid4(),
    # garantindo unicidade e segurança. Ele é salvo no perfil do usuário
    # e enviado por email para ser usado na redefinição de senha.
    token = str(uuid.uuid4())
    user.security_profile.reset_password_token = token
    user.security_profile.reset_password_expires = timezone.now() + timedelta(hours=1)
    user.security_profile.save()
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    subject = 'Recuperação de Senha - Nexum'
    #para alterar a mensagem de recuperação de senha, é na variavel message
    message = f"""
    <p>Olá <strong>{user.name}</strong>,</p>
    <p>Você solicitou a recuperação de senha.</p>
    <p>Clique no link abaixo para redefinir sua senha:</p>
    <p><a href="{reset_link}">Redefinir Minha Senha</a></p>
    <p><small>Este link expira em 1 hora.</small></p>
    """
    email_service = get_email_service()
    email_service.send_email(to=user.email, subject=subject, body=message)

class SanitizedCharField(serializers.CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return nh3.clean(data, tags=set())

class RichTextField(serializers.CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        allowed_tags = {
            'b', 'i', 'u', 'em', 'strong', 'a',
            'p', 'br', 'ul', 'ol', 'li', 'h3', 'h4'
        }
        allowed_attributes = {
            'a': {'href', 'title', 'target'},
        }
        return nh3.clean(data, tags=allowed_tags, attributes=allowed_attributes)