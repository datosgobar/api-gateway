# Generated by Django 2.0.1 on 2018-04-16 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_registry', '0017_auto_20180413_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='httplogdata',
            name='kong_id',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='jwtdata',
            name='kong_id',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='ratelimitingdata',
            name='kong_id',
            field=models.UUIDField(),
        ),
    ]
