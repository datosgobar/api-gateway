import requests
from requests.exceptions import ConnectionError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import ApiData


class DocsView(APIView):

    @staticmethod
    def get(_, name):
        url = ApiData.objects.get(name=name).documentation_url
        try:
            response = requests.get(url)
        except ConnectionError:
            data = 'Unable to connect to documentation server'
        else:
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
            else:
                data = 'Unable to retrieve documentation'
        return Response(data)
