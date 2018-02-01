from django_rq import job


@job('create_model')
def make_model_object(validated_data, serializer_class):
    serializer = serializer_class(data=validated_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
