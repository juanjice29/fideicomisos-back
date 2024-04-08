from django.test import TestCase

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from accounts.models import User, Profile, Role, View, Permisos
from .serializers import LoginSerializer
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("ALTER SESSION SET \"_ORACLE_SCRIPT\"=true;")
class LoginViewTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='C##testuser', password='testpassword')

    def test_login(self):
        # Prepare the data for the POST request
        data = {
            'username': 'C##testuser',
            'password': 'testpassword',
        }

        # Make a POST request to the login view
        response = self.client.post(reverse('public:login'), data)

        # Check if the response status code is 200 (HTTP OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data contains the 'access' and 'refresh' keys
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        pass
class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user
        self.user = User.objects.create_user(username='C##testuser', password='testpassword')

        # Create a role
        self.role = Role.objects.create(name='EMPLEADO')

        # Create a view
        self.view = View.objects.create(name='RestrictedView')

        # Create a profile for the user with the role
        self.profile = Profile.objects.create(user=self.user, rol=self.role)

        # Create a permission for the role to access the view
        self.permiso = Permisos.objects.create(role=self.role, view=self.view)

    def test_restricted_view(self):
        # Log in the user
        self.client.login(username='C##testuser', password='testpassword')

        # Make a GET request to the RestrictedView
        response = self.client.get(reverse('public:restricted'))

        # Check if the response status code is 200 (HTTP OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data is what you expect
        expected_data = {
            'user': {
                'username': 'C##testuser',
                'rol': 'EMPLEADO',
                'views': ['RestrictedView'],
            },
            # Add the expected 'access' and 'refresh' data here
        }
        self.assertEqual(response.data, expected_data)