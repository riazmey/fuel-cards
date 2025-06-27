
from django import forms
from cards.models import Site


class SiteAdminForm(forms.ModelForm):
    class Meta:

        fields = [
            'type',
            'url',
            'contract_id',
            'login',
            'password',
            'token']

        widgets = {
            'url': forms.URLInput(),
            'password': forms.PasswordInput(),
            'token': forms.PasswordInput()}

        model = Site
