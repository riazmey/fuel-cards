
from rest_framework import serializers

from .enum_transaction_type import SerializerEntityEnumTransactionType
from .site import SerializerEntitySite
from .card import SerializerEntityCard
from .transaction_item import SerializerEntityTransactionItem

from cards.models import Transaction

from cards.validators import (
    validate_common_site,
    validate_common_card)


class SerializerParamsTransactionSite(serializers.Serializer):
    site = serializers.IntegerField()
    begin = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, data):
        validate_common_site(data)
        return data

class SerializerParamsTransactionSiteCard(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    begin = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        return data


class SerializerEntityTransaction(serializers.ModelSerializer):

    site = SerializerEntitySite()
    type = SerializerEntityEnumTransactionType()
    card = SerializerEntityCard()
    items = SerializerEntityTransactionItem(many=True, source='transaction_relate_transaction_item')

    class Meta:

        fields = (
            'id_external',
            'site',
            'type',
            'date',
            'card',
            'details',
            'amount',
            'discount',
            'items')

        model = Transaction
