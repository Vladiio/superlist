import os
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(StaticLiveServerTestCase):

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

    def test_can_start_a_list_for_one_user(self):
        # Edith goes to new to-do app and check out its homepage
        self.browser.get(self.live_server_url)

        # Edith notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
                inputbox.get_attribute('placeholder'),
                'Enter a to-do item'
        )

        # She types "Buy peacock feathers" into a text box (Edith's hobby
        # is tying fly-fishing lures)
        inputbox.send_keys(self.first_item_row)

        # When she hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list
        inputbox.send_keys(Keys.ENTER) 
        self.wait_for_row_in_list_table('1: ' + self.first_item_row)

        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly" (Edith is very methodical)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys(self.second_item_row)

        # The page updates again, and now shows both items on her list
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: ' + self.first_item_row)
        self.wait_for_row_in_list_table('2: ' + self.second_item_row)

        # Satisfied, she goes back to sleep

    
    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith starts a new to-do list
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id("id_new_item")
        inputbox.send_keys(self.first_item_row)
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: " + self.first_item_row)
        
        # She notices that her list has a unique URL
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')
        
        # Now a new user, Francis, comes along to the site.

        ## We use a new browser session to make sure that no
        ## information of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Francis visits tho home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn(self.first_item_row, page_text)
        self.assertNotIn(self.second_item_row, page_text)

        # Francis starts a new list by entering a new item. He
        # is less interested then Edith...
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy milk")

        # Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        #Again, there is no trace of Edith's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn(self.first_item_row, page_text)
        self.assertIn("Buy milk", page_text)

        # Satisfied, they both go sleep

    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
                inputbox.location['x'] + inputbox.size['width'] / 2,
                512,
                delta=10
        )

        # She starts a new list and sees the input is nicely
        # centered there too
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
                inputbox.location['x'] + inputbox.size['width'] / 2,
                512,
                delta=10
        )

