
from rest_framework import serializers
from .item import SerializerEntityItem
from cards.models import TransactionItem


class SerializerEntityTransactionItem(serializers.ModelSerializer):

    item = SerializerEntityItem()

    class Meta:

        fields = (
            'item',
            'item_description',
            'quantity',
            'price',
            'price_with_discount',
            'amount',
            'amount_with_discount')

        model = TransactionItem
