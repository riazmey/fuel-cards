
from django.contrib import admin
from cards.forms import LimitAdminForm


class LimitAdmin(admin.ModelAdmin):

    fields = [
        'site',
        'card',
        ('id_external', 'deleted'),
        'type',
        'category',
        'item',
        'period',
        'unit',
        'value',
        'balance']

    list_display = [
        'site',
        'card',
        'id_external',
        'type',
        'period',
        'category',
        'value',
        'balance',
        'deleted']

    search_fields = ['card', 'id_external']
    list_filter = ['card']
    ordering = ['card', 'id_external']
    
    form = LimitAdminForm