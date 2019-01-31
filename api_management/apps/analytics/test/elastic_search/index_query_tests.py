from unittest.mock import patch


def test_index_query_after_save(query, httplogdata):
    with patch('api_management.apps.analytics.elastic_search.query_index.index_query')\
            as index_query_call:
        query.api_data.httplog = httplogdata
        query.save()
        assert index_query_call.assert_called_once
