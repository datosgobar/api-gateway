from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ApiData


class DocsView(APIView):

    renderer_classes = (TemplateHTMLRenderer,)

    @staticmethod
    def get(_, name):

        url = get_object_or_404(ApiData, name=name).documentation_url

        if not url:
            data = {'message': 'doc server not configured'}
            return Response(data, status=status.HTTP_404_NOT_FOUND, template_name="404.html")

        data = {'documentation_url': url}
        return Response(data, template_name="api_documentation.html")
