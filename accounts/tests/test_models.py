from django.test import TestCase
from django.contrib.auth import get_user_model, login

from accounts.models import Token


User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.email = 'test@example.com'

    def test_user_is_valid_with_email_only(self):
        user = User(email=self.email)
        user.full_clean()  # shouldn't rise

    def test_email_is_primary_key(self):
        user = User.objects.create(email=self.email)
        self.assertEqual(user.pk, self.email)

    def test_no_problem_with_auth_login(self):
        user = User.objects.create(email=self.email)
        user.backend = ''
        request = self.client.request().wsgi_request
        login(request, user) # shouldn't rise


class TokenModelTest(TestCase):

    def test_links_user_with_auto_generated_uid(self):
        token1 = Token.objects.create(email='test1@example.com')
        token2 = Token.objects.create(email='test2@example.com')
        self.assertNotEqual(token1.uid, token2.uid)