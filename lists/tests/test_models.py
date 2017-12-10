from django.test import TestCase

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
