from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@fff.com'
        password = 'test123'
        user = get_user_model()\
            .objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_email_normalized(self):
        """Test email for a new user is normalised"""
        email = "test@FFF.COM"
        user = get_user_model()\
            .objects.create_user(email=email, password='test')
        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email(self):
        """Test new user with invalid email fails"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test')

    def test_create_new_superuser(self):
        """Test createing a new superuser"""
        user = get_user_model().objects.\
            create_superuser('test@fff.com', 'test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
