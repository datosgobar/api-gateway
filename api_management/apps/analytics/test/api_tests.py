from django.urls import reverse
from rest_framework.test import APIClient

from api_management.apps.analytics.models import Query


def test_analytics_api_valid_query(staff_user, well_formed_query):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado responde con estado 201
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    response = client.post(reverse("query-list"), well_formed_query, format='json')
    assert response.status_code == 204


def test_analytics_api_invalid_query(staff_user):  # pylint: disable=invalid-name
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query con campos flatantes responde con estado 400
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    response = client.post(reverse("query-list"), {}, format='json')
    assert response.status_code == 400


def test_analytics_api_forbidden(user, well_formed_query):
    """
    Test cuando un user le pega al endpoint de queries
    responde con estado 403
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(reverse("query-list"), well_formed_query, format='json')
    assert response.status_code == 403


def test_analytics_api_unauthorized(well_formed_query):
    """
    Test cuando un user anonimo le pega al endpoint de queries
    responde con estado 401
    :return:
    """

    client = APIClient()
    response = client.post(reverse("query-list"), well_formed_query, format='json')
    assert response.status_code == 401


def test_create_model_query(staff_user, well_formed_query):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado crea un Query en el modelo
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    client.post(reverse("query-list"), well_formed_query, format='json')

    assert Query.objects.all().count() == 1


def test_query_has_status_code(staff_user, well_formed_query):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado crea un Query con un status code
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    client.post(reverse("query-list"), well_formed_query, format='json')

    query = Query.objects.all().first()
    assert query.status_code == well_formed_query['status_code']


def test_status_code_is_optional(staff_user, well_formed_query):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado crea un Query, sin requerir el status_code
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    well_formed_query.pop('status_code', None)
    client.post(reverse("query-list"), well_formed_query, format='json')

    query = Query.objects.all().first()
    assert query.status_code is None
