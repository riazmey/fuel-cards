
from django.utils import timezone


class WSDataSiteBalance:
    def __init__(self, **kwargs):
        self.date = kwargs.get('date', timezone.now())
        self.balance = kwargs.get('balance', 0.00)
        self.credit = kwargs.get('credit', 0.00)


class WSDataItem:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self.name = kwargs.get('name', '')
        self.category = kwargs.get('category', '')


class WSDataCard:
    def __init__(self, **kwargs):
        self.number = kwargs.get('number', '')
        self.status = kwargs.get('status', '')


class WSDataCardLimits:
    def __init__(self, **kwargs):
        self.card_number = kwargs.get('card_number', '')
        self.limits = []


class WSDataLimit:
    def __init__(self, **kwargs):
        self.card_number = kwargs.get('card_number', '')
        self.id_external = kwargs.get('id_external', '')
        self.type = kwargs.get('type', '')
        self.category = kwargs.get('category', '')
        self.item = kwargs.get('item', '')
        self.unit = kwargs.get('unit', '')
        self.period = kwargs.get('period', '')
        self.value = kwargs.get('value', 0.00)
        self.value_new = kwargs.get('value_new', 0.00)
        self.balance = kwargs.get('balance', 0.00)


class WSDataTransaction:
    def __init__(self, **kwargs):
        self.id_external = kwargs.get('id_external', '')
        self.type = kwargs.get('type', '')
        self.card_number = kwargs.get('card_number', '')
        self.date = kwargs.get('date', '')
        self.amount = kwargs.get('amount', 0.00)
        self.discount = kwargs.get('discount', 0.00)
        self.details = kwargs.get('details', '')
        self.items = kwargs.get('items', [])


class WSDataTransactionItem:
    def __init__(self, **kwargs):
        self.item = kwargs.get('item', '')
        self.item_description = kwargs.get('item_description', '')
        self.quantity = kwargs.get('quantity', 0.00)
        self.price = kwargs.get('price', 0.00)
        self.price_with_discount = kwargs.get('price_with_discount', 0.00)
        self.amount = kwargs.get('amount', 0.00)
        self.amount_with_discount = kwargs.get('amount_with_discount', 0.00)
