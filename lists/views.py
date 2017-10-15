from django.shortcuts import render, redirect

from lists.models import Item


def home_page(request):
    if request.method == "POST":
        item_text = request.POST.get('item_text', '')
        item = Item.objects.create(text=item_text)
        return redirect('/')

    items = Item.objects.all()
    return render(request, 'home.html', {'items': items})

