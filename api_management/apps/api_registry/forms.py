from django.forms import modelform_factory
from api_management.apps.api_registry.models import TokenRequest


# pylint: disable=invalid-name
TokenRequestForm = modelform_factory(TokenRequest,
                                     fields=('applicant',
                                             'contact_email',
                                             'consumer_application',
                                             'requests_per_day'))
