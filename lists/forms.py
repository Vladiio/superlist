from django import forms
from django.core.exceptions import ValidationError

from lists.models import Item, List

EMPTY_ITEM_ERROR = 'You can\'t have an empty list item'

DUPLICATE_ITEM_ERROR = 'You\'ve already got this in your list'


# class NewListForm(forms.ModelForm):
#     text = forms.CharField()
# 
#     class Meta:
#         model = List
#         fields = '__all__'
# 
#     def save(self, owner=None):
#         list = super().save()
#         item = Item(text=self.cleaned_data['text'])
#         item.save()
#         # if owner:
#         #   self.instance.owner = owner


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

    def save(self, for_list, **kwargs):
        self.instance.list = for_list
        return super().save(**kwargs)

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

    def save(self):
        return forms.models.ModelForm.save(self)
