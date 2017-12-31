from django.shortcuts import render, redirect

from lists.models import List
from lists.forms import ItemForm, ExistingListItemForm


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    item_form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        item_form = ExistingListItemForm(for_list=list_, data=request.POST)
        if item_form.is_valid():
            item_form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': item_form})


def new_list(request):
    item_form = ItemForm(data=request.POST)

    if item_form.is_valid():
        list_ = List.objects.create()
        item_form.save(list_)
        return redirect(list_)

    return render(request, 'home.html', {'form': item_form})
