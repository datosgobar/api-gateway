# Generated by Django 2.0.1 on 2018-09-14 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_auto_20180913_1026_squashed_0005_auto_20180913_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='request_method',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
    ]
