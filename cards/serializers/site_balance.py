
from rest_framework import serializers

from .site import SerializerEntitySite

from cards.models import SiteBalance
from cards.validators import validate_common_site


class SerializerParamsSiteBalanceSite(serializers.Serializer):
    site = serializers.IntegerField()

    def validate(self, data):
        validate_common_site(data)
        return data


class SerializerParamsSiteBalanceSiteDate(serializers.Serializer):
    site = serializers.IntegerField()
    date = serializers.DateField()

    def validate(self, data):
        validate_common_site(data)
        return data


class SerializerEntitySiteBalance(serializers.ModelSerializer):

    site = SerializerEntitySite()
    date = serializers.DateTimeField()

    class Meta:

        fields = (
            'id',
            'site',
            'date',
            'balance',
            'credit',
            'available')

        model = SiteBalance
