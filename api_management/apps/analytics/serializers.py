from rest_framework import serializers

from .models import Query


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = (
            'id', 'ip_address', 'host', 'uri', 'api_data',
            'querystring', 'start_time', 'request_time', 'status_code',
        )
