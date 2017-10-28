from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item, List


class ListAndItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self): 
        test_data = ('The first (ever) list item', 'Item the second')

        list_ = List.objects.create()
        for text in test_data:
            Item.objects.create(text=text, list=list_)

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), len(test_data))

        for index, text in enumerate(test_data): 
            self.assertEqual(saved_items[index].list, list_)
            self.assertEqual(saved_items[index].text, text)
        


class HomePageTest(TestCase):

    def setUp(self):
        self.text = 'A new list item'

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        response = self.client.get('/lists/the-only-list-in-the-world/')
        self.assertTemplateUsed(response, 'list.html')

    def test_display_all_items(self):
        list_ = List.objects.create()
        items = ('itemey 1', 'itemey 2')
        for item_text in items:
            Item.objects.create(text=item_text, list=list_)

        response = self.client.get('/lists/the-only-list-in-the-world/')

        for item_text in items:
            self.assertContains(response, items[0])
            self.assertContains(response, items[1])


class NewListTest(TestCase):
    
    def test_can_save_a_post_request(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        
        qs = Item.objects.all()
        self.assertEqual(qs.count(), 1)
        new_item = qs.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_post(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertRedirects(response, '/lists/the-only-list-in-the-world/')
    
