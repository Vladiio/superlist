import os
import time
from datetime import datetime

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from .server_tools import create_session_on_server, reset_database
from .management.commands.create_session import create_preauthenticated_session


SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps')

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
