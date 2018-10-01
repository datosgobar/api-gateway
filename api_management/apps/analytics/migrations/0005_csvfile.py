# Generated by Django 2.0.1 on 2018-09-21 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_query_request_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsvFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(max_length=30)),
                ('file_name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='analytics/')),
            ],
        ),
    ]
