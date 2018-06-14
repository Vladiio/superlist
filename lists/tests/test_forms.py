import unittest
from django.test import TestCase

from lists.forms import (
    ItemForm, EMPTY_ITEM_ERROR,
    ExistingListItemForm, DUPLICATE_ITEM_ERROR, NewListForm
)
from lists.models import List, Item


class NewListFormTest(unittest.TestCase):

    @unittest.mock.patch('lists.forms.Item')
    @unittest.mock.patch('lists.forms.List')
    def test_creates_new_list_on_form_save(self, mockList, mockItem):
        mock_list = mockList.return_value
        mock_item = mockItem.return_value
        user = unittest.mock.Mock()

        def check_item_text_and_list():
            self.assertEqual(mock_item.text, 'new item')
            self.assertEqual(mock_item.list, mock_list)
            self.assertTrue(mock_list.save.called)

        mock_item.save.side_effect = check_item_text_and_list

        form = NewListForm(data={'text': 'new item'})
        form.is_valid()
        form.save(owner=user)

        self.assertTrue(mock_item.save.called)


class ItemFormTest(TestCase):
    def test_form_renders_text_input(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_from_validation_for_blank_items(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_save_handles_saving_to_a_list(self):
        list_ = List.objects.create()
        form = ItemForm(data={'text': 'do me'})
        new_item = form.save(list_)
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'do me')
        self.assertEqual(new_item.list, list_)


class ExistingListItemFormTest(TestCase):

    def setUp(self):
        self.list = List.objects.create()

    def test_form_renders_item_text_input(self):
        form = ExistingListItemForm(for_list=self.list)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = ExistingListItemForm(for_list=self.list, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        item_text = 'test'
        Item.objects.create(list=self.list, text=item_text)
        form = ExistingListItemForm(for_list=self.list,
                                    data={'text': item_text})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])

    def test_form_save(self):
        list_ = List.objects.create()
        data = {'text': 'test'}
        form = ExistingListItemForm(for_list=list_, data=data)
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())
