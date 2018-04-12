from django.forms import modelform_factory
from api_management.apps.api_registry.models import TokenRequest


TokenRequestForm = modelform_factory(TokenRequest, exclude=[])
