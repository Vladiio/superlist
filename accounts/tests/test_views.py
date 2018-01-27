from django.test import TestCase
from django.core.urlresolvers import reverse

import accounts.views


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

    def test_sends_mail_to_address_from_post(self):
        self.send_mail_called = False

        def fake_send_mail(subject, body, from_email, to_list):
            self.send_mail_called = True
            self.subject = subject
            self.body = body
            self.from_email = from_email
            self.to_list = to_list

        accounts.views.send_mail = fake_send_mail
        self.post_data()

        self.assertTrue(self.send_mail_called)
        self.assertEqual(self.subject, 'Your login link for Superlists')
        self.assertEqual(self.from_email, 'noreply@superlists')
        self.assertEqual(self.to_list, [self.email])
