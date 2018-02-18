from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model

from .server_tools import create_session_on_server
from .management.commands.create_session import create_preauthenticated_session

from .base import FunctionalTest

User = get_user_model()


class MyListsTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(email)
        else:
            session_key = create_preauthenticated_session(email)
        ## to set a cookie we need to first visit the domain
        ## 404 pages load the quickest!
        self.browser.get(self.live_server_url + '/404_no_such_url/')
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))

    def test_logged_in_users_are_saved_as_my_lists(self):
        email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Edith is a logged in user
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)