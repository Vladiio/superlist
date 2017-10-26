from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item


class ItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        test_data = ('The first (ever) list item', 'Item the second')

        for text in test_data:
            Item.objects.create(text=text)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), len(test_data))

        for index, text in enumerate(test_data): 
            self.assertEqual(saved_items[index].text, text)
        


class HomePageTest(TestCase):

    def setUp(self):
        self.text = 'A new list item'

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_post_request(self):
        response = self.client.post('/', data={'item_text': self.text})
        
        qs = Item.objects.all()
        self.assertEqual(qs.count(), 1)
        new_item = qs.first()
        self.assertEqual(new_item.text, self.text)

    def test_redirects_after_post(self):
        response = self.client.post('/', data={'item_text': self.text})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/lists/the-only-list-in-the-world/')

    def test_only_saves_items_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)
    

class ListViewTest(TestCase):

    def test_uses_list_template(self):
        response = self.client.get('/lists/the-only-list-in-the-world/')
        self.assertTemplateUsed(response, 'list.html')

    def test_display_all_items(self):
        items = ('itemey 1', 'itemey 2')
        for item_text in items:
            Item.objects.create(text=item_text)

        response = self.client.get('/lists/the-only-list-in-the-world/')

        for item_text in items:
            self.assertContains(response, items[0])
            self.assertContains(response, items[1])

