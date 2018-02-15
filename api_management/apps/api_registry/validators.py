from django.core.validators import RegexValidator

import api_management.apps.api_registry.helpers as helpers


class HostsValidator(RegexValidator):

    def __init__(self):
        host_regex = r'(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?'
        hosts_validator_regex = helpers.coma_separated_list_of_regex(host_regex)

        super(HostsValidator, self).__init__(hosts_validator_regex,
                                             'Only domain names are allowed')


class UrisValidator(RegexValidator):

    def __init__(self):
        uri_regex = r'([/]{1}[\w\d]+)+\/?'
        uris_validator_regex = helpers.coma_separated_list_of_regex(uri_regex)

        super(UrisValidator, self).__init__(uris_validator_regex,
                                            'Only alphanumeric and _ characters are allowed. \n'
                                            'Must be prefixed with slash (/)')


class AlphanumericValidator(RegexValidator):

    def __init__(self):
        super(AlphanumericValidator, self).__init__(r'^[0-9a-zA-Z\.\_\~\\\-]+$',
                                                    'Only alphanumeric and . - _ ~ characters are allowed.')