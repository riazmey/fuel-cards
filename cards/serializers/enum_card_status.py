
from rest_framework import serializers
from cards.models import EnumCardStatus


class SerializerEntityEnumCardStatus(serializers.ModelSerializer):

    name = serializers.CharField(source='code_str')

    class Meta:

        fields = (
            'name',
            'repr')

        model = EnumCardStatus
