from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ApiData
from .forms import TokenRequestForm


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


class TokenRequestView(APIView):

    renderer_classes = (TemplateHTMLRenderer, )

    @staticmethod
    def get(_, form=None):
        return Response({'form': (form or TokenRequestForm())}, template_name="token_request.html")

    def post(self, request):
        form = TokenRequestForm(request.POST)

        if not form.is_valid():
            return self.get(request, form=form)

        form.save()
        return Response({}, template_name='token_request_success.html')
