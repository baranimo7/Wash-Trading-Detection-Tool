from django import forms
from collection.models import Collection


class SearchForm(forms.Form):
    collection = forms.CharField(label='Enter Your Collection:', max_length=100)
    collections = forms.ModelChoiceField(label='Collection Dropdown',
                                         queryset=Collection.objects.all(),
                                         required=False,
                                         initial=0)