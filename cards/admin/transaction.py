
from django.contrib import admin
from cards.forms import TransactionAdminForm


class TransactionAdmin(admin.ModelAdmin):

    fields = [
        'site',
        ('type', 'id_external'),
        'date',
        'card',
        'amount',
        'discount',
        'details']

    list_display = [
        'type',
        'date',
        'card',
        'id_external',
        'amount',
        'discount']

    search_fields = ['card', 'id_external']
    list_filter = ['card', 'type']
    ordering = ['-date', 'card']
    date_hierarchy = 'date'
    save_as = True
    
    form = TransactionAdminForm