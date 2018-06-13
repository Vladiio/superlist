from unittest.mock import patch, Mock
import unittest

from django.test import TestCase
from django.http import HttpRequest
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from lists.models import Item, List
from lists.forms import (
        ItemForm, EMPTY_ITEM_ERROR,
        ExistingListItemForm, DUPLICATE_ITEM_ERROR
)
from lists.views import new_list2


User = get_user_model()


class HomePageTest(TestCase):

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):

    def post_invalid_input(self):
        new_list = List.objects.create()
        return self.client.post(
                f'/lists/{new_list.id}/',
                data={'text': ''}
        )

    def post_data(self, data, list_=None):
        list_ = List.objects.create() if list_ is None else list_
        return self.client.post(f'/lists/{list_.id}/', data=data)

    def test_uses_list_template(self):
        new_list = List.objects.create()
        response = self.client.get(f'/lists/{new_list.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        item_list = ('other list item 1', 'other list item 2')
        for item in item_list:
            correct_list_ = List.objects.create()
            Item.objects.create(text=item, list=correct_list_)

        # get the last list
        response = self.client.get(f'/lists/{correct_list_.id}/')
        self.assertContains(response, item_list[1])
        self.assertNotContains(response, item_list[0])

    def test_passes_correct_list_to_template(self):
        List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):
        List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
                f'/lists/{correct_list.id}/',
                data={'text': 'A new list item'}
        )
        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renderes_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_displays_error(self):
        response = self.post_invalid_input()
        expected_error = escape(EMPTY_ITEM_ERROR)
        self.assertContains(response, expected_error)

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_displays_item_form(self):
        new_list = List.objects.create()
        response = self.client.get(f'/lists/{new_list.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        item_text = 'test'
        item = Item.objects.create(list=list_, text=item_text)
        response = self.post_data({'text': item_text}, list_=list_)

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.count(), 1)


@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'some text'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        new_list2(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        new_list_form = mockNewListForm.return_value
        new_list_form.is_valid.return_value = True
        new_list2(self.request)
        new_list_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
            self, mockRedirect, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid = True

        response = new_list2(self.request)
        self.assertEqual(response, mockRedirect.return_value)
        mockRedirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_rerenders_homepage_template_if_form_invalid(
            self, mockRender, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid = False
        response = new_list2(self.request)
        self.assertEqual(response, mockRender.return_value)
        mockRender.assert_called_once_with(
                self.request, 'home.html', {'form': mock_form }
        )

    def test_does_not_save_form_if_one_invalid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid = False
        new_list2(self.request)
        self.assertFalse(mock_form.save.called)


class NewListIntegratedTest(TestCase):

    @unittest.skip
    def test_list_owner_is_saved_if_user_is_authenticated(
        self, mockItemFormClass, mockListClass
    ):
        user = User.objects.create(email='me@example.com')
        self.client.force_login(user)
        # mock_list = mockListClass.return_value

        # def check_owner_assigned():
        #     self.assertEqual(mock_list.owner, user)
        # mock_list.save.side_effect = check_owner_assigned

        self.client.post('/lists/new', data={'text': 'A new list item'})
        mock_list.save.assert_called_once_with()

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new',
                                    data={'text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)


class MyListsTest(TestCase):

    def setUp(self):
        self.email = 'edith@example.com'
        self.user = User.objects.create(email=self.email)

    def request_get(self, *args, **kwargs):
        url = reverse('my_lists', args=(self.email,))
        return self.client.get(url, *args, **kwargs)

    def test_renders_correct_template(self):
        response = self.request_get()
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='someuser@example.com')
        response = self.request_get()
        self.assertEqual(response.context['owner'], self.user)
