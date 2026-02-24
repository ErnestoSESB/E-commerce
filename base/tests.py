from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import BaseCustomUser, Cart, UserSecurityProfile

class SecurityTests(APITestCase):
    def setUp(self):
        self.client_user = BaseCustomUser.objects.create_user(
            username='client', email='client@test.com', password='password123', user_type='client')
        self.staff_user = BaseCustomUser.objects.create_user(
            username='admin', email='admin@test.com', password='password123', user_type='admin')
        self.other_client = BaseCustomUser.objects.create_user(
            username='other', email='other@test.com', password='password123', user_type='client')

    def test_normal_user_cannot_filter_sensitive_data(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('user-list')
        response = self.client.get(url, {'email': 'admin@test.com'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Acesso negado', str(response.data))

    def test_staff_user_can_filter_sensitive_data(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('user-list')
        response = self.client.get(url, {'email': 'client@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_only_see_own_cart(self):
        Cart.objects.create(user=self.client_user)
        Cart.objects.create(user=self.other_client)
        self.client.force_authenticate(user=self.client_user)
        url = reverse('cart-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        cart_owner_id = response.data['results'][0]['user']
        self.assertEqual(str(cart_owner_id), str(self.client_user.id))

        def test_user_cannot_access_others_cart(self):
            Cart.objects.create(user=self.client_user)
            Cart.objects.create(user=self.other_client)
            self.client.force_authenticate(user=self.client_user)
            url = reverse('cart-detail', args=[Cart.objects.get(user=self.other_client).id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertIn('Acesso negado', str(response.data))

        def test_anonymous_cannot_create_transaction(self):
            url = reverse('financial-transaction-list')
            data = {"amount": 100, "type": "purchase"}
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIn('Authentication credentials were not provided', str(response.data))

    def test_normal_user_cannot_access_financial_transactions(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('financial-transaction-list')   
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user_can_access_financial_transactions(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('financial-transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TwoFactorAuthTests(APITestCase):
    def setUp(self):
        self.user_without_2fa = BaseCustomUser.objects.create_user(
            username='user1', email='user1@test.com', password='password123')
        self.user_with_2fa = BaseCustomUser.objects.create_user(
            username='user2', email='user2@test.com', password='password123')
        self.user_with_2fa.security_profile.is_2fa_enabled = True
        self.user_with_2fa.security_profile.save()

    def test_login_without_2fa_returns_tokens(self):
        url = reverse('token_obtain_pair')
        data = {'email': 'user1@test.com', 'password': 'password123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_2fa_requires_otp(self):
        url = reverse('token_obtain_pair')
        data = {'email': 'user2@test.com', 'password': 'password123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('2fa_required'))
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_verify_otp_with_valid_code(self):
        profile = self.user_with_2fa.security_profile
        profile.otp_code = '123456'
        profile.otp_created_at = timezone.now()
        profile.save()
        
        url = reverse('verify_2fa')
        data = {'email': 'user2@test.com', 'otp_code': '123456'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_verify_otp_with_invalid_code(self):
        profile = self.user_with_2fa.security_profile
        profile.otp_code = '123456'
        profile.otp_created_at = timezone.now()
        profile.save()
        
        url = reverse('verify_2fa')
        data = {'email': 'user2@test.com', 'otp_code': '999999'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('inválido', str(response.data))

    def test_verify_otp_with_expired_code(self):
        profile = self.user_with_2fa.security_profile
        profile.otp_code = '123456'
        profile.otp_created_at = timezone.now() - timedelta(minutes=11)
        profile.save()
        url = reverse('verify_2fa')
        data = {'email': 'user2@test.com', 'otp_code': '123456'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expirado', str(response.data))

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = BaseCustomUser.objects.create_user(
            username='testuser', email='test@test.com', password='oldpassword123')

    def test_request_password_reset(self):
        url = reverse('password_reset_request')
        data = {'email': 'test@test.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email existir', str(response.data))

    def test_request_password_reset_nonexistent_email(self):
        url = reverse('password_reset_request')
        data = {'email': 'nonexistent@test.com'}
        response = self.client.post(url, data)
        # Deve retornar a mesma mensagem por segurança
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_with_valid_token(self):
        profile = self.user.security_profile
        profile.reset_password_token = 'valid-token-123'
        profile.reset_password_expires = timezone.now() + timedelta(hours=1)
        profile.save()
        
        url = reverse('password_reset')
        data = {'token': 'valid-token-123', 'new_password': 'newpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se a senha foi alterada
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_reset_password_with_invalid_token(self):
        url = reverse('password_reset')
        data = {'token': 'invalid-token', 'new_password': 'newpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('inválido', str(response.data))

    def test_reset_password_with_expired_token(self):
        profile = self.user.security_profile
        profile.reset_password_token = 'expired-token'
        profile.reset_password_expires = timezone.now() - timedelta(hours=1)
        profile.save()
        
        url = reverse('password_reset')
        data = {'token': 'expired-token', 'new_password': 'newpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expirado', str(response.data))

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProtectedHelloView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Olá, {request.user.username}! Você está autenticado."})