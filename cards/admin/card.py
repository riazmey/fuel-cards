
from django.contrib import admin
from cards.forms import CardAdminForm


class CardAdmin(admin.ModelAdmin):

    fields = [
        'site',
        'number',
        'relevant',
        'status']

    list_display = [
        'site',
        'number',
        'relevant',
        'status']

    search_fields = ['number']
    list_filter = ['site']
    ordering = ['site', 'number']
    
    form = CardAdminForm