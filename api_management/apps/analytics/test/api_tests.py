import pytest
from django.urls import reverse
from faker import Faker
from rest_framework.test import APIClient

from api_management.apps.analytics.models import Query
from api_management.apps.analytics.test.conftest import query_dict
from api_management.apps.analytics.test.support import query_dict_response

faker = Faker()  # pylint: disable=invalid-name


# pylint: disable=unused-argument
def test_analytics_api_valid_query(staff_user, well_formed_query, httplogdata):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado responde con estado 201
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    response = client.post(reverse("query-list"), well_formed_query, format='json')
    assert response.status_code == 204


def test_analytics_invalid_query(staff_user):
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


# pylint: disable=unused-argument
def test_create_model_query(staff_user, well_formed_query, httplogdata):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado crea un Query en el modelo
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    client.post(reverse("query-list"), well_formed_query, format='json')

    assert Query.objects.all().count() == 1


# pylint: disable=unused-argument
def test_query_has_status_code(staff_user, well_formed_query, httplogdata):
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


# pylint: disable=unused-argument
def test_status_code_is_optional(staff_user, well_formed_query, httplogdata):
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


# pylint: disable=unused-argument
def test_query_has_api_data_id(staff_user, well_formed_query, api_data, httplogdata):
    """
    Test cuando un staff_user le pega al endpoint de queries
    con un json de query bien formado crea un Query con un status code
    :return:
    """

    client = APIClient()
    client.force_authenticate(user=staff_user)
    well_formed_query['api_data'] = api_data.id
    client.post(reverse("query-list"), well_formed_query, format='json')

    query = Query.objects.all().first()
    assert query.api_data.pk == api_data.pk


QUERY1 = query_dict(faker, 1, 1, start_time="2017-04-27T10:50:58-03:00")

QUERY2 = query_dict(faker, 1, 2, start_time="2018-04-27T10:50:58-03:00")

QUERY3 = query_dict(faker, 1, 3, start_time="2019-04-27T10:50:58-03:00")

QUERIES_FILTERED = [

    (
        [],
        {},
        [],
    ),
    (
        [QUERY1, QUERY2],
        {},
        [query_dict_response(QUERY1), query_dict_response(QUERY2)],
    ),
    (
        [QUERY1, QUERY2],
        {'from_date': '2018-01-31'},
        [query_dict_response(QUERY2)]
    ),
    (
        [QUERY1, QUERY2],
        {'to_date': '2018-01-31'},
        [query_dict_response(QUERY1)]
    ),
    (
        [QUERY1],
        {'kong_api_id': '1'},
        []
    ),
    (
        [QUERY1, QUERY2, QUERY3],
        {'from_date': '2018-01-31',
         'to_date': '2019-01-31'},
        [query_dict_response(QUERY2)]
    ),
]


# pylint: disable=unused-argument, too-many-arguments
@pytest.mark.parametrize("queries, filter_applied, expected_results",
                         QUERIES_FILTERED)
def test_filter_queries(staff_user,
                        queries,
                        filter_applied,
                        expected_results,
                        api_data,
                        httplogdata):
    """
    Test al hacer get en el endpoint de queries
    con parametros de filtrado
    retorna queries que cumplen
    con los filtros de forma paginada
    :return:
    """
    # Setup
    client = APIClient()
    client.force_authenticate(user=staff_user)
    for query in queries:
        query['api_data'] = api_data.id
        client.post(reverse("query-list"), query, format='json')
    for result in expected_results:
        result['api_data'] = api_data.id

    # Exercise
    response = client.get(reverse("query-list"),
                          data=filter_applied,
                          format="json")

    # Verify
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['count'] == len(expected_results)
    assert response_json['results'] == expected_results
