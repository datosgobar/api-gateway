import pytest
from django.core.exceptions import ValidationError

from api_management.apps.api_registry.models import ACCEPTED, KongConsumer

pytestmark = pytest.mark.django_db


def test_request_accepted(token_request):
    token_request.accept()
    assert token_request.state == ACCEPTED


def test_request_cant_accept_twice(token_request):
    token_request.accept()
    with pytest.raises(ValidationError):
        token_request.accept()


def test_request_cant_reject_if_accepted(token_request):
    token_request.accept()
    with pytest.raises(ValidationError):
        token_request.reject()


def test_request_cant_accept_if_rejected(token_request):
    token_request.reject()
    with pytest.raises(ValidationError):
        token_request.accept()


def test_request_cant_accept_if_consumer_already_exists(token_request):
    consumer = KongConsumer.objects.create_from_request(token_request)
    consumer.save()
    with pytest.raises(ValidationError):
        token_request.accept()
