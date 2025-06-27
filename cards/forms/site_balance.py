
from django import forms
from cards.models import SiteBalance


class SiteBalanceAdminForm(forms.ModelForm):
    class Meta:

        fields = [
            'site',
            'date',
            'balance',
            'credit',
            'available']

        model = SiteBalance
