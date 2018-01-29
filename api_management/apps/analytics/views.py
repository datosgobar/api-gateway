import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def create_query(request):
    json.loads(request.body)
    return HttpResponse(status=201)
