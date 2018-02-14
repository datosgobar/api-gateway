import string

from faker.providers import BaseProvider


class CustomInfoProvider(BaseProvider):

    def api_name(self):
        return self.generator.name().replace(' ', '')

    def api_path(self):
        path = self.generator.uri_path()
        if not path.startswith('/'):
            path = '/%s' % path
        return path

    def kong_id(self, grouping=(8, 4, 4, 4, 12),
                valid_elements=tuple(string.ascii_lowercase + string.digits)):
        """
            Generates a random kong_id
            Example: "14656344-9e38-4315-8ae2-c23551ea3b9d"
        :return:
        """
        chars = []
        for group in grouping:
            chars += self.random_sample(elements=valid_elements, length=group)
            chars += "-"
        chars.pop()
        return "".join(chars)
