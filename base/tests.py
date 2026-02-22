from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import BaseCustomUser, Cart

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
