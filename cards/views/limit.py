
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cards.models import (
    Site,
    Card,
    Limit)

from cards.serializers import (
    SerializerEntityLimit,
    SerializerParamsLimitSite,
    SerializerParamsLimitSiteCard,
    SerializerParamsLimitPostTypeAll,
    SerializerParamsLimitPostTypeCategory,
    SerializerParamsLimitPostTypeItem,
    SerializerParamsLimitPut,
    SerializerParamsLimitDelete)

from ws.sites import WSDataLimit


class LimitAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        card_number = request.query_params.get('card', None)
        deleted = request.query_params.get('deleted', None)
        direct = request.query_params.get('direct', False)
        
        if card_number:
            params = SerializerParamsLimitSiteCard(data=request.query_params)
        else:
            params = SerializerParamsLimitSite(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_obj = Site.objects.get(id=params.data.get('site'))

        if direct:
            if card_number:
                data, success = site_obj.ws.limits_get(cards=[Card.objects.get(site=site_obj, number=card_number)])
            else:
                data, success = site_obj.ws.limits_get()
            if not success:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

        if card_number:
            card_obj = Card.objects.get(site=site_obj, number=card_number)
            if deleted is None:
                queryset = Limit.objects.filter(card=card_obj)
            else:
                queryset = Limit.objects.filter(card=card_obj, deleted=deleted)
        else:
            if deleted is None:
                queryset = Limit.objects.filter(site=site_obj)
            else:
                queryset = Limit.objects.filter(site=site_obj, deleted=deleted)

        if queryset:
            return Response(SerializerEntityLimit(queryset, many=True).data)
        else:
            return Response([])

    def post(self, request):
        type = request.query_params.get('type', '').lower()

        if not type:
            message = 'В параметрах HTTP запроса не указан обязательный параметр type ' \
                + '(тип лимита топливной карты)'
            raise serializers.ValidationError(message)

        match type:
            case 'category':
                params = SerializerParamsLimitPostTypeCategory(data=request.query_params)
            case 'item':
                params = SerializerParamsLimitPostTypeItem(data=request.query_params)
            case _:
                params = SerializerParamsLimitPostTypeAll(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_obj = Site.objects.get(id=params.data.get('site'))

        data, success = site_obj.ws.limit_add(
            WSDataLimit(
                card_number = params.data.get('card'),
                id_external = '',
                type = type,
                category = params.data.get('category', '').lower(),
                item = params.data.get('item', '').lower(),
                unit = params.data.get('unit').lower(),
                period = params.data.get('period').lower(),
                value = float(params.data.get('value'))
            ))

        if success:
            return Response(SerializerEntityLimit(data).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

    def put(self, request):
        params = SerializerParamsLimitPut(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        card_number = params.data.get('card')
        id_external = params.data.get('id_external')
        value_new = float(params.data.get('value'))

        site_obj = Site.objects.get(id=site_id)
        card_obj = Card.objects.get(site=site_obj, number=card_number)
        limit_obj = Limit.objects.get(site=site_obj, card=card_obj, id_external=id_external)
        
        if limit_obj.category:
            category = limit_obj.category.code_str
        else:
            category = ''

        if limit_obj.item:
            item = limit_obj.item.id_external
        else:
            item = ''

        data, success = site_obj.ws.limit_update(
            WSDataLimit(
                card_number = card_number,
                id_external = id_external,
                type = limit_obj.type.code_str,
                category = category,
                item = item,
                unit = limit_obj.unit,
                period = limit_obj.period.code_str,
                value = limit_obj.value,
                value_new = value_new)
        )

        if success:
            return Response(SerializerEntityLimit(data).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

    def delete(self, request):
        params = SerializerParamsLimitDelete(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        card_number = params.data.get('card')
        id_external = params.data.get('id_external')

        site_obj = Site.objects.get(id=site_id)
        data, success = site_obj.ws.limit_delete(card_number=card_number, id_external=id_external)

        if success:
            return Response(data, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')
        
