import re
import time
import poplib
import os

from django.core import mail
from selenium.webdriver.common.keys import Keys


from .base import FunctionalTest


SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):

    def test_can_get_email_link_to_log_in(self):
        if self.staging_server:
            test_email = 'vlad.mashkin@yahoo.com'
        else:
            test_email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(test_email)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text

        ))

        # email = mail.outbox[0]
        # self.assertIn(test_email, email.to)
        # self.assertEqual(email.subject, SUBJECT)
        body = self.wait_for_email(test_email, SUBJECT)

        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)
        self.browser.get(url)
        self.wait_to_be_logged_in(test_email)

        # now she logs out
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_to_be_logged_out(test_email)

    def wait_for_email(self, test_email, subject):
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start_time = time.time()
        inbox = poplib.POP3_SSL(host='pop.mail.yahoo.com')
        try:
            inbox.user(test_email)
            inbox.pass_(os.environ.get('YEMAIL_PWD'))
            while time.time() - start_time < 60:
                # get 10 newest messages
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 5), count + 1)):
                    print('getting message ', i)
                    _, lines, _ = inbox.retr(i)
                    lines = [line.decode('utf-8') for line in lines]
                    if f'Subject: {subject}' in lines:
                        email_id = i
                        return '\n'.join(lines)
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()

