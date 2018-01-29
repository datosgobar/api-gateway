from api_management.apps.common.utils import same


def test_returns_the_same(a_random_string):
    """
    Test example of using py.test and a fixture created in conftest.py
    :param a_random_string:
    :return:
    """
    assert same(a_random_string) == a_random_string
