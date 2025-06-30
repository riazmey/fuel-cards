
from rest_framework import serializers

from .enum_limit_type import SerializerEntityEnumLimitType
from .enum_item_category import SerializerEntityEnumItemCategory
from .enum_limit_period import SerializerEntityEnumLimitPeriod
from .enum_card_status import SerializerEntityEnumCardStatus
from .site import SerializerEntitySite
from .card import SerializerEntityCard
from .item import SerializerEntityItem

from cards.models import Card
from cards.models import Limit

from cards.validators import (
    validate_common_site,
    validate_common_card,
    validate_common_limit_type,
    validate_common_category,
    validate_common_item,
    validate_common_period,
    validate_common_unit,
    validate_limit_id_external,
    validate_limit_deleted)


class SerializerParamsLimitSite(serializers.Serializer):
    site = serializers.IntegerField()

    def validate(self, data):
        validate_common_site(data)
        return data


class SerializerParamsLimitSiteCard(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        return data


class SerializerParamsLimitPostTypeAll(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    type = serializers.CharField()
    period = serializers.CharField()
    unit = serializers.CharField()
    value = serializers.FloatField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        validate_common_limit_type(data)
        validate_common_period(data)
        validate_common_unit(data)
        return data


class SerializerParamsLimitPostTypeCategory(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    type = serializers.CharField()
    category = serializers.CharField()
    period = serializers.CharField()
    unit = serializers.CharField()
    value = serializers.FloatField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        validate_common_limit_type(data)
        validate_common_category(data)
        validate_common_period(data)
        validate_common_unit(data)
        return data


class SerializerParamsLimitPostTypeItem(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    type = serializers.CharField()
    item = serializers.CharField()
    period = serializers.CharField()
    unit = serializers.CharField()
    value = serializers.FloatField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        validate_common_limit_type(data)
        validate_common_item(data)
        validate_common_period(data)
        validate_common_unit(data)
        return data


class SerializerParamsLimitPut(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    id_external = serializers.CharField()
    value = serializers.FloatField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        validate_limit_id_external(data)
        validate_limit_deleted(data)
        return data


class SerializerParamsLimitDelete(serializers.Serializer):
    site = serializers.IntegerField()
    card = serializers.CharField()
    id_external = serializers.CharField()

    def validate(self, data):
        validate_common_site(data)
        validate_common_card(data)
        validate_limit_id_external(data)
        validate_limit_deleted(data)
        return data


class SerializerEntityLimit(serializers.ModelSerializer):

    site = SerializerEntitySite()
    card = SerializerEntityCard()
    type = SerializerEntityEnumLimitType()
    category = SerializerEntityEnumItemCategory()
    item = SerializerEntityItem()
    period = SerializerEntityEnumLimitPeriod()

    class Meta:

        fields = (
            'site',
            'card',
            'id_external',
            'type',
            'category',
            'item',
            'period',
            'unit',
            'value',
            'balance',
            'deleted')

        model = Limit


class SerializerEntityCardWithLimits(serializers.ModelSerializer):

    site = SerializerEntitySite()
    status = SerializerEntityEnumCardStatus()
    limits = SerializerEntityLimit(many=True, source='card_relate_limit')

    class Meta:

        fields = (
            'id',
            'site',
            'number',
            'status',
            'relevant',
            'limits')

        model = Card