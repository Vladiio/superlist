from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model

from .base import FunctionalTest

User = get_user_model()


class MyListsTest(FunctionalTest):

    def test_logged_in_users_are_saved_as_my_lists(self):
        # Edith is a logged in user
        self.create_pre_authenticated_session('edith@example.com')

        # she goes to the home page and starts a new list
        self.browser.get(self.live_server_url)
        self.add_list_item(self.first_item_row)
        self.add_list_item(self.second_item_row)
        first_list_url = self.browser.current_url

        # she notices a "My lists" link for the first time
        self.browser.find_element_by_link_text('My lists').click()
        # she sees her list here and it's named accordingly
        # to its first list item
        self.wait_for(
            lambda: self.browser.find_element_by_link_text(self.first_item_row)
        )
        self.browser.find_element_by_link_text(self.first_item_row).click()
        self.assertEqual(first_list_url, self.browser.current_url)

        # she decides to start a new list just to see
        self.browser.get(self.live_server_url)
        self.add_list_item('New item')
        second_list_url = self.browser.current_url

        # unser My lists her list appears
        self.browser.find_element_by_link_text('My lists').click()
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('New item')
        )
        self.browser.find_element_by_link_text('New item').click()
        self.wait_for(
            lambda: self.assertEqual(second_list_url, self.browser.current_url)
        )
        # she logs out and My lists option disappears
        self.browser.find_element_by_link_text('Log out').click()
        # self.wait_for(lambda: self.assertEqual(
        #     self.browser.find_element_by_link_text('My lists'),
        #     []
        # ))
