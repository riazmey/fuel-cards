
from rest_framework import serializers
from cards.models import EnumTransactionType


class SerializerEntityEnumTransactionType(serializers.ModelSerializer):

    name = serializers.CharField(source='code_str')

    class Meta:

        fields = (
            'name',
            'repr')

        model = EnumTransactionType
