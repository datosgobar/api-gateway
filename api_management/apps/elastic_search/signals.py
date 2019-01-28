from django.db.models.signals import post_save
from django.dispatch import receiver

from api_management.apps.analytics.models import Query


@receiver(post_save, sender=Query)
def index_query(_sender, instance, **_kwargs):
    instance.index()
