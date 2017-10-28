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

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        item_list = (
                ('itemey 1', 'itemey 2'),
                ('other list item 1', 'other list item 2'),
        )
        for item in item_list:
            correct_list_ = List.objects.create()
            Item.objects.create(text=item[0], list=correct_list_)
            Item.objects.create(text=item[1], list=correct_list_)

        response = self.client.get(f'/lists/{correct_list_.id}/')

        # we use other list items instead of etemey 1 and 2 due to loop above
        self.assertContains(response, item_list[1][0])
        self.assertContains(response, item_list[1][1])
        self.assertNotContains(response, item_list[0][0])
        self.assertNotContains(response, item_list[0][1])

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')


class NewItemTest(TestCase):

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
                f'/lists/{correct_list.id}/add_item', 
                data={'item_text': 'A new list item'}
        )
        self.assertRedirects(response, f'/lists/{correct_list.id}/')
    
