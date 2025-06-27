
from rest_framework import serializers

from .enum_site_type import SerializerEntityEnumSiteType

from cards.models import Site
from cards.validators import validate_common_site


class SerializerParamsSite(serializers.Serializer):
    site = serializers.IntegerField()

    def validate(self, data):
        validate_common_site(data)
        return data


class SerializerEntitySite(serializers.ModelSerializer):

    type = SerializerEntityEnumSiteType()

    class Meta:

        fields = (
            'id',
            'type',
            'url',
            'contract_id',
            'login')

        model = Site