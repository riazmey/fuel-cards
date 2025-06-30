
from rest_framework import serializers

from .enum_card_status import SerializerEntityEnumCardStatus
from .site import SerializerEntitySite

from cards.models import Card

from cards.validators import (
    validate_common_site,
    validate_common_card,
    validate_common_card_status)


class SerializerParamsCardSite(serializers.Serializer):
    site = serializers.IntegerField()

    def validate(self, data):
        validate_common_site(data)
        return data

class SerializerParamsCardSiteCard(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        return data


class SerializerParamsCardSiteStatus(serializers.Serializer):
    site = serializers.IntegerField()
    status = serializers.CharField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card_status(data)
        return data


class SerializerParamsCardSiteCardStatus(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    status = serializers.CharField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        validate_common_card_status(data)
        return data


class SerializerEntityCard(serializers.ModelSerializer):

    site = SerializerEntitySite()
    status = SerializerEntityEnumCardStatus()

    class Meta:

        fields = (
            'id',
            'site',
            'number',
            'status',
            'relevant')

        model = Card
