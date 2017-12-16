from django.test import TestCase
from django.core.exceptions import ValidationError

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

    def test_cannot_save_empty_list_item(self):
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_get_absolute_url(self):
        new_list = List.objects.create()
        self.assertEqual(new_list.get_absolute_url(), f'/lists/{new_list.id}/')
