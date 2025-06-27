
from django import forms
from cards.models import Limit
from ws.classifiers import WSClassifiers


class LimitAdminForm(forms.ModelForm):

    ws = WSClassifiers()

    unit = forms.ChoiceField(
        choices = ws.list_units({'type':'weight'}) + ws.list_units({'type':'economic'}),
        initial = '383')

    class Meta:

        fields = [
            'site',
            'card',
            'id_external',
            'deleted',
            'type',
            'category',
            'item',
            'period',
            'unit',
            'value',
            'balance']

        model = Limit
