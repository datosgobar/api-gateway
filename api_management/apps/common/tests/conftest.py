import random
import string

import pytest


@pytest.fixture
def a_random_string(char_numbers=10):
    return ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=char_numbers
    ))
