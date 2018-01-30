from rest_framework import serializers
from api_management.apps.analytics.models import Query


class QuerySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    ip_address = serializers.CharField(max_length=200, allow_null=True)
    host = serializers.CharField()
    uri = serializers.CharField()
    querystring = serializers.CharField()
    start_time = serializers.DateTimeField()
    request_time = serializers.DurationField()

    def create(self, validated_data):
        return Query.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.ip_address = validated_data.get('ip_address', instance.ip_address)
        instance.host = validated_data.get('host', instance.host)
        instance.uri = validated_data.get('uri', instance.uri)
        instance.querystring = validated_data.get('querystring', instance.querystring)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.request_time = validated_data.get('request_time', instance.request_time)
        instance.save()
        return instance
