from django.test import TestCase

from lists.forms import (
        ItemForm, EMPTY_ITEM_ERROR,
        ExistingListItemForm, DUPLICATE_ITEM_ERROR
)
from lists.models import List, Item


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
