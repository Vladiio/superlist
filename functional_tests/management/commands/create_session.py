from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import BaseCommand
from django.conf import settings


User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        email = options.get('email')
        session_key = create_preauthenticated_session(email)
        self.stdout.write(session_key)

    def add_arguments(self, parser):
        parser.add_argument('email')


def create_preauthenticated_session(email):
    user = User.objects.create(email=email)
    session = SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    return session.session_key
