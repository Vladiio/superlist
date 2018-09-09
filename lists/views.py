from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from lists.models import List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm


User = get_user_model()


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
    new_list_form = NewListForm(data=request.POST)
    if new_list_form.is_valid():
        new_list = new_list_form.save(owner=request.user)
        return redirect(new_list)
    return render(request, 'home.html', {'form': new_list_form })


def my_lists(request, user_email):
    owner = User.objects.get(email=user_email)
    return render(request, 'my_lists.html', {'owner': owner})
