# Generated by Django 2.0.1 on 2018-02-15 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_registry', '0002_auto_20180215_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='apidata',
            name='preserve_host',
            field=models.BooleanField(default=False),
        ),
    ]