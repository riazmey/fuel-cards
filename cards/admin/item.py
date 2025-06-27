
from django.contrib import admin
from cards.forms import ItemAdminForm


class ItemAdmin(admin.ModelAdmin):

    fields = [
        'site',
        'id_external',
        'category',
        'name']

    list_display = [
        'name',
        'site',
        'category']

    search_fields = ['name']
    list_filter = ['site']
    ordering = ['site', 'name']
    
    form = ItemAdminForm