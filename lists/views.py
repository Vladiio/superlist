from django.shortcuts import render, redirect

from lists.models import List
from lists.forms import ItemForm


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    item_form = ItemForm()

    if request.method == 'POST':
        item_form = ItemForm(data=request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.list = list_
            item.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': item_form})


def new_list(request):
    item_form = ItemForm(data=request.POST)

    if item_form.is_valid():
        list_ = List.objects.create()
        item = item_form.save(commit=False)
        item.list = list_
        item.save()
        return redirect(list_)

    return render(request, 'home.html', {'form': item_form})
