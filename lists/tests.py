from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from lists.views import home_page


class SmokeTest(TestCase):

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_post_request(self):
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('A new list item', response.content.decode())

