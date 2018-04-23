import requests

from django.core.exceptions import ValidationError


class KongConsumerChildMixin:

    @staticmethod
    def endpoint(kong_client, kong_consumer, consumer_attribute):
        if kong_consumer.kong_id is None:
            raise ValidationError("kong_consumer kong_id can't be null")

        return '%s%s/%s/' % (kong_client.consumers.endpoint,
                             kong_consumer.get_kong_id(),
                             consumer_attribute)

    def send_create(self, kong_client, kong_consumer, consumer_attribute, data=None):
        endpoint = self.endpoint(kong_client, kong_consumer, consumer_attribute)

        response = requests.post(endpoint, data=data)
        json = response.json()
        if response.status_code != 201:
            raise ConnectionError(json)
        return json

    @staticmethod
    def send_delete(endpoint):
        response = requests.delete(endpoint)
        if response.status_code != 204:
            raise ConnectionError()
