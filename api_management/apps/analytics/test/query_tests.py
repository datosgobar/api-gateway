def test_query_has_params(query, cfaker):
    query_string = "empty=&value=1&many=2,3&multiple=1&multiple=2"
    query.querystring = query_string
    assert query.params() == {"empty": "", "value": "1", "many": "2,3", "multiple": "2"}


def test_query_without_params(query):
    query_string = ""
    query.querystring = query_string
    assert query.params() == {}
