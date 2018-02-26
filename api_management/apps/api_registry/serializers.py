from rest_framework import serializers

from .models import ApiData


class ApiDocSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApiData
        fields = ('name', 'documentation_url',)
