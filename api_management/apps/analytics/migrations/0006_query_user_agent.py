# Generated by Django 2.0.1 on 2018-04-06 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0005_auto_20180327_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='user_agent',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]