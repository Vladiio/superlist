from unittest.mock import patch, call

from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.models import Token


class SendLoginEmailViewTest(TestCase):

    def setUp(self):
        self.url = reverse('send_login_email')
        self.email = 'test@example.com'

    def post_data(self):
        data = {'email': self.email}
        return self.client.post(self.url, data=data)

    def test_redirects_to_home_page(self):
        response = self.post_data()
        self.assertRedirects(response, '/')

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        self.post_data()
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, [self.email])

    @patch('accounts.views.messages')
    def test_adds_success_message(self, mock_messages):
        response = self.post_data()
        expected = call(response.wsgi_request, 'Check your email')
        self.assertEqual(expected, mock_messages.success.call_args)

    def test_creates_token_associated_with_email(self):
        self.post_data()
        token = Token.objects.first()
        self.assertEqual(token.email, self.email)

    @patch('accounts.views.send_mail')
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
        self.post_data()
        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login/?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)


@patch('accounts.views.auth')
class LoginViewTest(TestCase):

    def setUp(self):
        self.token = 'abcd123'
        self.url = f'/accounts/login/?token={self.token}'

    def test_redirects_to_home_page(self, mock_auth):
        response = self.client.post(self.url)
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        self.client.get(self.url)
        self.assertEqual(call(token_uid=self.token),
                         mock_auth.authenticate.call_args)

    def test_calls_auth_login_with_user_if_there_is_one(self, mock_auth):
        response = self.client.get(self.url)
        self.assertEqual(
            mock_auth.login.call_args,
            call(response.wsgi_request, mock_auth.authenticate.return_value)
        )

    def test_does_not_login_if_user_is_now_authenticated(self, mock_auth):
        mock_auth.authenticate.return_value = None
        self.client.get(self.url)
        self.assertFalse(mock_auth.login.called)