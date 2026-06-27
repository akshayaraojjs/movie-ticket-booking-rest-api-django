from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class AccountsAPITests(APITestCase):
    
    def setUp(self):
        # Create standard customer
        self.customer = User.objects.create_user(
            username="customer_test",
            email="customer@example.com",
            password="testpassword123",
            role="customer",
            phone="1234567890"
        )
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@example.com",
            password="adminpassword123",
            role="admin",
            phone="9876543210"
        )
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")
        self.change_password_url = reverse("accounts:change-password")

    def test_registration_success_default_customer(self):
        data = {
            "username": "new_customer",
            "email": "new_customer@example.com",
            "password": "customerpass123!",
            "confirm_password": "customerpass123!",
            "phone": "5551234567",
            "first_name": "New",
            "last_name": "Customer"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "new_customer")
        self.assertEqual(response.data["role"], "customer")
        
        # Verify db persistence
        user = User.objects.get(username="new_customer")
        self.assertTrue(user.check_password("customerpass123!"))

    def test_registration_fails_duplicate_username_or_email(self):
        # Duplicate username
        data = {
            "username": "customer_test",
            "email": "another@example.com",
            "password": "customerpass123!",
            "confirm_password": "customerpass123!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

        # Duplicate email
        data = {
            "username": "another_user",
            "email": "customer@example.com",
            "password": "customerpass123!",
            "confirm_password": "customerpass123!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_fails_passwords_mismatch(self):
        data = {
            "username": "mismatch_user",
            "email": "mismatch@example.com",
            "password": "password123!",
            "confirm_password": "password456!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_anonymous_cannot_register_admin_or_manager(self):
        data = {
            "username": "rogue_admin",
            "email": "rogue_admin@example.com",
            "password": "roguepass123!",
            "confirm_password": "roguepass123!",
            "role": "admin"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.data)

    def test_admin_can_register_manager(self):
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "username": "new_manager",
            "email": "manager@example.com",
            "password": "managerpass123!",
            "confirm_password": "managerpass123!",
            "role": "theatre_manager"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "theatre_manager")

    def test_login_success_via_username(self):
        data = {
            "username_or_email": "customer_test",
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertEqual(response.data["user"]["username"], "customer_test")

    def test_login_success_via_email(self):
        data = {
            "username_or_email": "customer@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertEqual(response.data["user"]["email"], "customer@example.com")

    def test_login_fails_invalid_credentials(self):
        data = {
            "username_or_email": "customer_test",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("tokens", response.data)

    def test_profile_retrieval_requires_authentication(self):
        # Unauthenticated request
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_retrieval_success_when_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "customer_test")
        self.assertEqual(response.data["role"], "customer")

    def test_profile_update_success(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "first_name": "UpdatedName",
            "last_name": "UpdatedLast",
            "phone": "9999999999",
            "username": "customer_test",
            "email": "customer@example.com"
        }
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "UpdatedName")
        self.assertEqual(response.data["phone"], "9999999999")
        
        # Verify db change
        user = User.objects.get(id=self.customer.id)
        self.assertEqual(user.first_name, "UpdatedName")
        self.assertEqual(user.phone, "9999999999")

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "old_password": "testpassword123",
            "new_password": "newsecurepassword123!",
            "confirm_new_password": "newsecurepassword123!"
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

        # Verify old password fails login and new password succeeds
        login_data = {
            "username_or_email": "customer_test",
            "password": "newsecurepassword123!"
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_change_password_fails_incorrect_old_password(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "old_password": "incorrectpassword",
            "new_password": "newsecurepassword123!",
            "confirm_new_password": "newsecurepassword123!"
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)
