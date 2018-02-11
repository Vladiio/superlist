from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token


User = get_user_model()


class AuthenticationTestBase(TestCase):

    def setUp(self):
        self.email = 'email@example.com'
        self.authentication_backend = PasswordlessAuthenticationBackend()


class AuthenticateTest(AuthenticationTestBase):

    def test_returns_none_if_no_such_token(self):
        result = self.authentication_backend.authenticate('no-such-token')
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        token = Token.objects.create(email=self.email)
        authenticated_user = self.authentication_backend.authenticate(token.uid)
        created_user = User.objects.get(email=self.email)
        self.assertEqual(authenticated_user, created_user)

    def test_returns_existing_user_if_token_exists(self):
        new_user = User.objects.create(email=self.email)
        token = Token.objects.create(email=self.email)
        authenticated_user = self.authentication_backend.authenticate(token.uid)
        self.assertEqual(new_user, authenticated_user)


class GetUserTest(AuthenticationTestBase):

    def setUp(self):
        super().setUp()

    def test_returns_user_if_exists(self):
        User.objects.create(email='extra@example.com')
        new_user = User.objects.create(email=self.email)
        authenticated_user = self.authentication_backend.get_user(self.email)
        self.assertEqual(new_user, authenticated_user)

    def test_returns_none_if_user_does_not_exist(self):
        self.assertIsNone(
            self.authentication_backend.get_user(self.email)
        )