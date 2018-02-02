from django.db import models


class Api(models.Model):
    name = models.CharField(unique=True, max_length=200)
    upstream_url = models.URLField()
    uri = models.CharField(max_length=200)
    enabled = models.BooleanField()
