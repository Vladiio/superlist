import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def wait(func):
    def wrapper(*args, **kwargs):
        max_wait = 10
        start_time = time.time()
        while True:
            try:
                return func(*args, **kwargs)
            except (AssertionError, WebDriverException) as err:
                if time.time() - start_time > max_wait:
                    raise err
                time.sleep(0.5)
    return wrapper


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://{}'.format(staging_server)
        self.first_item_row = 'Buy peacock feathers'
        self.second_item_row = 'Use peacock feathers to make a fly'
        self.MAX_WAIT = 10

    def tearDown(self):
        self.browser.quit()

    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > self.MAX_WAIT:
                    raise e
                time.sleep(0.5)
    @wait
    def wait_for(self, func):
        func()

    @wait
    def wait_to_be_logged_in(self, email):
        self.browser.find_element_by_link_text('Log out')
        self.assertIn(
            email, self.browser.find_element_by_css_selector('.navbar').text
        )

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element_by_name('email')
        self.assertNotIn(
            email, self.browser.find_element_by_css_selector('.navbar').text
        )
