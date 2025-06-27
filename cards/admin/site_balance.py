
from django.contrib import admin
from cards.forms import SiteBalanceAdminForm


class SiteBalanceAdmin(admin.ModelAdmin):

    fields = [
        'site',
        'date',
        'balance',
        'credit',
        'available']

    list_display = [
        'site',
        'date',
        'available']

    list_filter = ['site']
    ordering = ['site', '-date']
    date_hierarchy = 'date'
    
    form = SiteBalanceAdminForm