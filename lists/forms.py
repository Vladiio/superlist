from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from lists.models import Item, List

User = get_user_model()

EMPTY_ITEM_ERROR = 'You can\'t have an empty list item'

DUPLICATE_ITEM_ERROR = 'You\'ve already got this in your list'


class SharedWithForm(forms.Form):
    share = forms.EmailField()

    def save(self, list_):
        email = self.cleaned_data['share']
        share_to = User.objects.get(email=email)
        list_.shared_with.add(share_to)
        return list_


class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg',
            }),
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR}
        }


class NewListForm(ItemForm):

    def save(self, owner):
        first_item_text = self.cleaned_data['text']
        if owner.is_authenticated:
            return List.create_new(first_item_text=first_item_text, owner=owner)
        else:
            return List.create_new(first_item_text=first_item_text)


class ExistingListItemForm(ItemForm):

    def __init__(self, for_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)
