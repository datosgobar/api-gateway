from django.db import migrations


def add_missing_consumer(apps, _):
    KongApiPluginJwt = apps.get_model('api_registry', 'KongApiPluginJwt')
    KongConsumer = apps.get_model('api_registry', 'KongConsumer')

    for kongapipluginjwt in KongApiPluginJwt.objects.filter(anonymous_consumer=None):
        KongConsumer.objects.create(enabled=True,
                                    api=kongapipluginjwt.parent,
                                    applicant="anonymous",
                                    contact_email="anon@anon.com")\
            .save()


class Migration(migrations.Migration):
    dependencies = [
        ('api_registry', '0010_auto_20180615_1101'),
    ]

    operations = [
        migrations.RunPython(add_missing_consumer),
    ]
