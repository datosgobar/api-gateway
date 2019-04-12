import pytest
from dateutil import relativedelta
from django.utils import timezone
from faker import Faker

from api_management.apps.analytics.csv_analytics.metrics_calculator \
    import IndicatorMetricsCalculator
from api_management.apps.analytics.models import Query
from api_management.apps.api_registry.models import KongApi


def create_query_in_time(a_time, kong_api):
    Query(id=Faker().random_number(), start_time=a_time, request_time=1,
          host='foo', uri='foo', user_agent='foo', api_data=kong_api).save()


def create_queries_and_calculator():
    calculator = IndicatorMetricsCalculator('series')
    kong_api = KongApi(name='series', upstream_url='foo')
    kong_api.save()
    for _x in range(0, 3):
        create_query_in_time(timezone.now(), kong_api)

    return calculator


@pytest.mark.django_db
def test_first_query_time(*_args):
    calculator = create_queries_and_calculator()

    query = Query.objects.last()  # update the latest, but it should be the first query time
    query.start_time = query.start_time - relativedelta.relativedelta(years=1)
    query.save()

    assert calculator.first_query_time() == Query.objects.last().start_time.date()


@pytest.mark.django_db
def test_total_unique_users_query():
    calculator = create_queries_and_calculator()

    expected_query_search = {
        'aggs': {
            'unique_users': {
                'cardinality': {'field': 'api_session_id'}
                }
            },
        'query': {
            'bool': {
                'filter': [
                    {
                        'terms': {'_id': [q.id for q in Query.objects.all()]}
                    }
                ]
            }
        }
    }

    es_query = calculator.generate_unique_users_query(Query.objects.all())

    assert es_query.search.to_dict() == expected_query_search
