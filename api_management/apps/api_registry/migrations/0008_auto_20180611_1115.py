# Generated by Django 2.0.1 on 2018-06-11 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_registry', '0007_auto_20180611_1110'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='KongPluginRateLimiting',
            new_name='KongApiPluginRateLimiting',
        ),
    ]
