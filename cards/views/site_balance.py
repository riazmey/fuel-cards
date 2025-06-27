
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cards.models import (
    Site,
    SiteBalance)

from cards.serializers import (
    SerializerEntitySiteBalance,
    SerializerParamsSiteBalanceSite,
    SerializerParamsSiteBalanceSiteDate)


class SiteBalanceAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        
        date = request.query_params.get('date', None)
        direct = request.query_params.get('direct', False)

        if date:
            params = SerializerParamsSiteBalanceSiteDate(data=request.query_params)
        else:
            params = SerializerParamsSiteBalanceSite(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_obj = Site.objects.get(id=params.data.get('site'))

        if direct:
            data, success = site_obj.ws.balance_get()
            if not success:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data, content_type='text/plain')

        if date:
            queryset = SiteBalance.objects.filter(site=site_obj, date__lte=date).order_by('-date')
        else:
            queryset = SiteBalance.objects.filter(site=site_obj).order_by('-date')

        if queryset:
            data = queryset[0]
        else:
            data = SiteBalance(site=site_obj, date=date)

        return Response(SerializerEntitySiteBalance(data).data)
