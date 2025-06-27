
from rest_framework import serializers
from cards.models import EnumItemCategory


class SerializerEntityEnumItemCategory(serializers.ModelSerializer):

    name = serializers.CharField(source='code_str')

    class Meta:

        fields = (
            'name',
            'repr')

        model = EnumItemCategory
