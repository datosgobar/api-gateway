from faker import Faker

from api_management.libs.providers.providers import CustomInfoProvider


def custom_faker():
    # Custom Fake
    a_faker = Faker()
    a_faker.add_provider(CustomInfoProvider)
    return a_faker
