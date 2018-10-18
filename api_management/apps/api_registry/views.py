from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.views.generic import View
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from .models import KongApi, KongApiPluginJwt, RootKongApi
from .forms import TokenRequestForm


class DocsView(APIView):

    renderer_classes = (TemplateHTMLRenderer,)

    @staticmethod
    def get(_, name):

        api = get_object_or_404(KongApi, name=name)
        if api.use_swagger:
            return DocsView.swager_documentation(api)

        return HttpResponseRedirect(api.documentation_url)

    @staticmethod
    def swager_documentation(api):
        url = api.documentation_url

        if not url:
            data = {'message': 'doc server not configured'}
            return Response(data, status=status.HTTP_404_NOT_FOUND, template_name="404.html")

        data = {'documentation_url': url,
                'api_name': api.name}

        try:
            data['token_required'] = api.kongapipluginjwt.enabled
        except KongApiPluginJwt.DoesNotExist:
            data['token_required'] = False

        return Response(data, template_name="api_documentation.html")


class TokenRequestView(View):

    @staticmethod
    def get(request, name, form=None):

        get_object_or_404(KongApi, name=name)

        return render(request,
                      "token_request.html",
                      {'api_name': name,
                       'form': (form or TokenRequestForm())})

    def post(self, request, name):
        form = TokenRequestForm(request.POST)

        if not form.is_valid():
            return self.get(request, name, form=form)

        token_request = form.save(commit=False)
        token_request.api = get_object_or_404(KongApi, name=name)
        token_request.save()

        return render(request, 'token_request_success.html', {})


def root_redirect(request):
    return HttpResponseRedirect(RootKongApi.get_solo().upstream_url)
