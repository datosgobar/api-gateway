from rest_framework import serializers

from .models import KongApi


class KongApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = KongApi
        fields = (
            'name', 'upstream_url', 'uri'
        )
