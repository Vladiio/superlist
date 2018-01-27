from django.conf.urls import url

from accounts.views import send_login_email


urlpatterns = [
    url(r'^send_login_email/$', send_login_email, name='send_login_email'),
]
