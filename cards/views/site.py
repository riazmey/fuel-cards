
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cards.models import Site

from cards.serializers import (
    SerializerEntitySite,
    SerializerParamsSite)


class SiteAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        params = SerializerParamsSite(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        site_obj = Site.objects.get(id=site_id)

        return Response(SerializerEntitySite(site_obj).data)
