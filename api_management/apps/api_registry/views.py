from json import JSONDecodeError
import requests
from requests.exceptions import ConnectionError  # pylint: disable=redefined-builtin
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import ApiData


class DocsView(APIView):

    renderer_classes = (TemplateHTMLRenderer,)
    template_name = "404.html"

    @staticmethod
    def get(_, name):
        try:
            url = ApiData.objects.get(name=name).documentation_url
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not url:
            data = {'message': 'doc server not configured'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        try:
            response = requests.get(url)
        except ConnectionError:
            data = {'message': 'Unable to connect to documentation server'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if response.status_code != status.HTTP_200_OK:
            data = {'message': 'Unable to retrieve documentation'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            json = response.json()
        except JSONDecodeError:
            data = {'message': "doc server response can't be json decoded"}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = {'api_name': name, 'data': json}
        return Response(data, template_name="api_documentation.html")
