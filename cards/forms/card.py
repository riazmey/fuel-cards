
from django import forms
from cards.models import Card


class CardAdminForm(forms.ModelForm):
    class Meta:

        fields = [
            'site',
            'number',
            'relevant',
            'status']

        model = Card
