# Generated by Django 2.0.1 on 2018-12-12 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0008_apisessionsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorCsvGeneratorTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('logs', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='csvfile',
            name='type',
            field=models.CharField(choices=[('analytics', 'analytics'), ('indicators', 'indicators')], default='analytics', max_length=30),
            preserve_default=False,
        ),
    ]
