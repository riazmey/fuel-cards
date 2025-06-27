
from django import forms
from cards.models import Transaction


class TransactionAdminForm(forms.ModelForm):
    class Meta:

        fields = [
            'site',
            'type',
            'id_external',
            'date',
            'card',
            'amount',
            'discount',
            'details']

        widgets = {'details': forms.Textarea()}
        model = Transaction
