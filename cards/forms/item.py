
from django import forms
from cards.models import Item


class ItemAdminForm(forms.ModelForm):
    class Meta:

        fields = [
            'site',
            'id_external',
            'category',
            'name']

        model = Item
