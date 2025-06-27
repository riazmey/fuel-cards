
from dateutil import parser

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cards.models import (
    Site,
    Card,
    Transaction)

from cards.serializers import (
    SerializerEntityTransaction,
    SerializerParamsTransactionSite,
    SerializerParamsTransactionSiteCard)


class TransactionAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        
        card_number = request.query_params.get('card', None)
        direct = request.query_params.get('direct', False)

        if card_number:
            params = SerializerParamsTransactionSiteCard(data=request.query_params)
        else:
            params = SerializerParamsTransactionSite(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_obj = Site.objects.get(id=params.data.get('site'))
        begin = params.data.get('begin')
        end = params.data.get('end')

        if direct:
            datetime_begin = parser.parse(begin).replace(tzinfo=None)
            datetime_end = parser.parse(end).replace(tzinfo=None, hour=23, minute=59, second=59)
            if card_number:
                data, success = site_obj.ws.transactions_get(card_number=card_number, begin=datetime_begin, end=datetime_end)
            else:
                data, success = site_obj.ws.transactions_get(begin=datetime_begin, end=datetime_end)
            if not success:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

        if card_number:
            card_obj = Card.objects.get(site=site_obj, number=card_number)
            queryset = Transaction.objects.filter(card=card_obj, date__gte=begin, date__lte=end)
        else:
            queryset = Transaction.objects.filter(site=site_obj, date__gte=begin, date__lte=end)
        if queryset:
            return Response(SerializerEntityTransaction(queryset, many=True).data)
        else:
            return Response([])
    