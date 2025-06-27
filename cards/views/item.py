
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cards.models import Site, Item

from cards.serializers import (
    SerializerEntityItem,
    SerializerParamsItemSite)


class ItemAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        params = SerializerParamsItemSite(data=request.query_params)
        params.is_valid(raise_exception=True)

        direct = request.query_params.get('direct', False)
        site_obj = Site.objects.get(id=params.data.get('site'))

        if direct:
            data, success = site_obj.ws.items_get()
            if not success:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

        queryset = Item.objects.filter(site__id=params.data.get('site'))
        if queryset:
            return Response(SerializerEntityItem(queryset, many=True).data)
        else:
            message = f'Не удалсь найти ни одного товара/услуги с переданными параметрами: {request.query_params}'
            raise serializers.ValidationError(message)
