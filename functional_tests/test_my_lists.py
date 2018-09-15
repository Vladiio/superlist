from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model

from .server_tools import create_session_on_server
from .management.commands.create_session import create_preauthenticated_session

from .base import FunctionalTest

User = get_user_model()


class MyListsTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_preauthenticated_session(email)
        ## to set a cookie we need to first visit the domain
        ## 404 pages load the quickest!
        self.browser.get(self.live_server_url + '/404_no_such_url/')
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))

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
        self.fail()
        # self.wait_for(lambda: self.assertEqual(
        #     self.browser.find_element_by_link_text('My lists'),
        #     []
        # ))
