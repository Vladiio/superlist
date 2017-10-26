from django.shortcuts import render, redirect

from lists.models import Item


def home_page(request):
    if request.method == "POST":
        item_text = request.POST.get('item_text', '')
        item = Item.objects.create(text=item_text)
        return redirect('/lists/the-only-list-in-the-world/')

    return render(request, 'home.html')


def view_list(request):
    items = Item.objects.all()
    return render(request, 'list.html', {'items': items})

