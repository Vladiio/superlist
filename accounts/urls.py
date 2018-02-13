from django.conf.urls import url
from django.contrib.auth.views import logout

from accounts.views import send_login_email, login_view


urlpatterns = [
    url(r'^send_login_email/$', send_login_email, name='send_login_email'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
]
