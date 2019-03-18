from elasticsearch_dsl import A


class Aggregations:

    @classmethod
    def cardinality(cls, field: str):
        return A('cardinality', field=field)
