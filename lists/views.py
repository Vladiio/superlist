from django.shortcuts import render
from django.http import HttpResponse


def home_page(request):
    submitted_item = request.POST.get('item_text', '')
    return render(request, 'home.html', {'new_item_text': submitted_item})

