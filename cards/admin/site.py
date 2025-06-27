
from django.contrib import admin
from cards.forms import SiteBalanceAdminForm


class SiteAdmin(admin.ModelAdmin):

    fields = [
        'type',
        'url',
        'contract_id',
        'login',
        'password',
        'token']

    list_display = [
        'type',
        'url',
        'login']

    search_fields = [
        'url',
        'login']

    list_filter = ['type']
    ordering = ['type']
    form = SiteBalanceAdminForm
