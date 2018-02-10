from unittest.mock import patch, call

from django.test import TestCase
from django.core.urlresolvers import reverse


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
        expected = call('Your login link for Superlists',
                        'body text tbc', 'noreply@superlists',
                        [self.email])
        self.assertTrue(mock_send_mail.called)
        self.assertEqual(expected, mock_send_mail.call_args)

    @patch('accounts.views.messages')
    def test_adds_success_message(self, mock_messages):
        response = self.post_data()
        expected = call(response.wsgi_request, 'Check your email')
        self.assertEqual(expected, mock_messages.success.call_args)