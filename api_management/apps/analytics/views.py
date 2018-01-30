from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes, api_view, \
    authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO

from api_management.apps.analytics.serializers import QuerySerializer


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAdminUser,))
def create_query(request):
    try:
        content = request.body
        stream = BytesIO(content)
        data = JSONParser().parse(stream)
    except ParseError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = QuerySerializer(data=data)

    if serializer.is_valid():
        query = serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    content = {
        'query': query,
    }
    return Response(content, status=status.HTTP_201_CREATED)
