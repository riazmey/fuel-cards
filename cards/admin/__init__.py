
from django.contrib import admin

from cards.models import (
    Site,
    Card,
    Item,
    Limit,
    SiteBalance,
    Transaction,
    TransactionItem)

from .site import SiteAdmin
from .card import CardAdmin
from .item import ItemAdmin
from .limit import LimitAdmin
from .site_balance import SiteBalanceAdmin
from .transaction import TransactionAdmin
from .transaction_item import TransactionItemAdmin


admin.site.register(Site, SiteAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(SiteBalance, SiteBalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionItem, TransactionItemAdmin)