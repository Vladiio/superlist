from django.test import TestCase
from django.core.exceptions import ValidationError

from lists.models import Item, List


class ItemModelTest(TestCase):

    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())

    def test_cannot_save_empty_list_item(self):
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_item_are_invalid(self):
        list_ = List.objects.create()
        item_name = 'test'
        Item.objects.create(list=list_, text=item_name)
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text=item_name)
            item.full_clean()

    def test_can_save_same_items_to_different_lists(self):
        item_name = 'test'
        list_one = List.objects.create()
        list_two = List.objects.create()
        Item.objects.create(list=list_one, text=item_name)
        item = Item(list=list_two, text=item_name)
        item.full_clean()  # shouldn't raise

    def test_list_ordering(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='i1')
        item2 = Item.objects.create(list=list1, text='item 2')
        item3 = Item.objects.create(list=list1, text='3')
        self.assertEqual(
                list(Item.objects.all()),
                [item1, item2, item3]
        )

    def test_string_representation(self):
        item = Item(text='some text')
        self.assertEqual(str(item), 'some text')


class ListModelTest(TestCase):

    def test_get_absolute_url(self):
        new_list = List.objects.create()
        self.assertEqual(new_list.get_absolute_url(), f'/lists/{new_list.id}/')
