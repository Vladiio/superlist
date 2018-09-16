from selenium import webdriver

from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage


def quit_if_possible(browser):
    try: browser.quite()
    except: pass


class SharingTest(FunctionalTest):
    def test_can_share_a_list_with_another_user(self):
        # Edith is a logged in user
        self.create_pre_authenticated_session('edith.example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # her friend is also hanging out on the lists site
        oni_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser
        self.create_pre_authenticated_session('oni@example.com')

        # edith goes to the home page and start a list
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('Get help')

        # she notices a share this list option
        share_box = list_page.get_share_box()
        self.assertEqual(share_box.get_attribute('placeholder'), 'your-friend@example.com')
        list_page.share_list_with('oni@example.com')

        # Oni now goes to the lists page with his browser
        self.browser = oni_browser
        MyListsPage(self).get_to_my_lists_page()
        # He sees Edith list in here
        self.browser.find_element_by_link_text('Get help').click()
        self.wait_for(lambda: self.assertEqual(
            list_page.get_list_owner(),
            'edith@example.com'
        ))
        # He adds an item to the list
        list_page.add_list_item('Hi Edith')

        # When Edith refreshes the page, she sees Oni's addition
        self.browser = edith_browser
        self.browser.refresh()
        list_page.wait_for_row_in_list_table('Hi Edith', 2)
