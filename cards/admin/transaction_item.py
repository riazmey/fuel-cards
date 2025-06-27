
from django.contrib import admin
from cards.forms import TransactionItemAdminForm


class TransactionItemAdmin(admin.ModelAdmin):

    fields = [
        'transaction',
        'item',
        'item_description',
        'quantity',
        ('price', 'price_with_discount'),
        ('amount', 'amount_with_discount')]

    list_display = [
        'transaction',
        'item',
        'amount']

    search_fields = ['transaction__id_external', 'item']
    list_filter = ['item']
    ordering = ['transaction', 'amount']
    save_as = True
    
    form = TransactionItemAdminForm