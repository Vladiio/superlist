import os
import time
from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from .server_tools import reset_database

SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps')

def wait(func):
    def wrapper(*args, **kwargs):
        max_wait = 20
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
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = 'http://{}'.format(self.staging_server)
            reset_database(self.staging_server)
        self.first_item_row = 'Buy peacock feathers'
        self.second_item_row = 'Use peacock feathers to make a fly'
        self.MAX_WAIT = 10

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix;
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown()

    def _test_has_failed(self):
        return any(error for (method, error) in self._outcome.errors)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        class_name = self.__class__.__name__
        return f'{SCREEN_DUMP_LOCATION}/{class_name}.{self._testMethodName}-window{self._windowid}-{timestamp}'

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print('Scrinshotting to ', filename)
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print('Dumping page HTML to ', filename)
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)

    def add_list_item(self, text):
        items_count = len(
            self.browser.find_elements_by_css_selector('#id_list_table tr')
        )
        self.get_item_input_box().send_keys(text)
        self.get_item_input_box().send_keys(Keys.ENTER)

        ordinal_number = items_count + 1
        self.wait_for_row_in_list_table(f'{ordinal_number}: {text}')

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
