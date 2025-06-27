
from django import forms
from cards.models import TransactionItem


class TransactionItemAdminForm(forms.ModelForm):
    class Meta:

        fields = [
            'transaction',
            'item',
            'item_description',
            'quantity',
            'price',
            'price_with_discount',
            'amount',
            'amount_with_discount']

        widgets = {'details': forms.Textarea()}
        model = TransactionItem
