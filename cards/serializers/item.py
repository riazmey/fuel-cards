
from rest_framework import serializers

from .site import SerializerEntitySite
from .enum_item_category import SerializerEntityEnumItemCategory

from cards.models import Item
from cards.validators import validate_common_site


class SerializerParamsItemSite(serializers.Serializer):
    site = serializers.IntegerField()

    def validate(self, data):
        validate_common_site(data)
        return data


class SerializerEntityItem(serializers.ModelSerializer):

    site = SerializerEntitySite()
    category = SerializerEntityEnumItemCategory()

    class Meta:

        fields = (
            'id',
            'site',
            'id_external',
            'category',
            'name')

        model = Item
