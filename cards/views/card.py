
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cards.models import (
    Site,
    Card,
    EnumCardStatus)

from cards.serializers import (
    SerializerEntityCard,
    SerializerParamsCardSite,
    SerializerParamsCardSiteCard,
    SerializerParamsCardSiteStatus,
    SerializerParamsCardSiteCardStatus)


class CardAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        
        status_name = request.query_params.get('status', None)
        card_number = request.query_params.get('card', None)
        direct = request.query_params.get('direct', False)

        if status_name and card_number:
            params = SerializerParamsCardSiteCardStatus(data=request.query_params)
        elif status_name and not card_number:
            params = SerializerParamsCardSiteStatus(data=request.query_params)
        elif not status_name and card_number:
            params = SerializerParamsCardSiteCard(data=request.query_params)
        else:
            params = SerializerParamsCardSite(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_obj = Site.objects.get(id=params.data.get('site'))

        if direct:
            data, success = site_obj.ws.cards_get()
            if not success:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

        if status_name and card_number:
            status_obj = EnumCardStatus.objects.get(code_str=status_name)
            query_params = {'site': site_obj, 'number': card_number,
                            'status': status_obj, 'relevant': True}
        elif status_name and not card_number:
            status_obj = EnumCardStatus.objects.get(code_str=status_name)
            query_params = {'site': site_obj, 'status': status_obj, 'relevant': True}
        elif not status_name and card_number:
            query_params = {'site': site_obj, 'number': card_number, 'relevant': True}
        else:
            query_params = {'site': site_obj, 'relevant': True}

        queryset = Card.objects.filter(**query_params)

        if queryset:
            return Response(SerializerEntityCard(queryset, many=True).data)
        else:
            if query_params:
                message = f'Couldn\'t find a fuel cards with params: {query_params}'
            else:
                message = f'There are no entries the fuel cards in the database.'
            raise serializers.ValidationError(message)


class CardStatusAPIView(APIView):

    def put(self, request):
        params = SerializerParamsCardSiteCardStatus(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_obj = Site.objects.get(id=params.data.get('site'))

        data, success = site_obj.ws.card_status_update(
            card_number = params.data.get('card'),
            status = params.data.get('status'))

        if success:
            return Response(SerializerEntityCard(data).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')
