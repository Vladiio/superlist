from django.core.mail import send_mail
from django.contrib import messages
from django.contrib import auth

from django.shortcuts import redirect, reverse

from accounts.models import Token


def send_login_email(request):
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = '{}?token={}'.format(reverse('login'), token.uid)
    absolute_url = request.build_absolute_uri(url)
    messages.success(request, 'Check your email')
    send_mail(
        'Your login link for Superlists',
        'Use this link to log in\n\n{}'.format(absolute_url),
        'noreply@superlists',
        [email],

    )
    return redirect('/')


def login_view(request):
    uid = request.GET.get('token')
    user = auth.authenticate(token_uid=uid)
    if user:
        auth.login(request, user)
    return redirect('/')