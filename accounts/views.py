from django.core.mail import send_mail
from django.contrib import messages

from django.shortcuts import redirect


def send_login_email(request):
    email = request.POST['email']
    messages.success(request, 'Check your email')
    send_mail(
        'Your login link for Superlists',
        'Use this link to log in',
        'noreply@superlists',
        [email],

    )
    return redirect('/')
