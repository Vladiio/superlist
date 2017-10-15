from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item


class ItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        test_data = ('The first (ever) list item', 'Item the second')

        for text in test_data:
            item = Item()
            item.text = text
            item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), len(test_data))

        for index, text in enumerate(test_data): 
            self.assertEqual(saved_items[index].text, text)
        


class SmokeTest(TestCase):

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_post_request(self):
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('A new list item', response.content.decode())

