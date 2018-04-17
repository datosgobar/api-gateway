# Generated by Django 2.0.1 on 2018-04-17 19:37

import api_management.apps.api_registry.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_registry', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JwtCredential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(null=True)),
                ('key', models.CharField(max_length=100, null=True)),
                ('secret', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='KongConsumer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False)),
                ('kong_id', models.UUIDField(null=True)),
                ('applicant', models.CharField(max_length=100)),
                ('contact_email', models.EmailField(max_length=254)),
                ('api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_registry.KongApi')),
            ],
            bases=(api_management.apps.api_registry.models.ManageKongOnSaveMixin, api_management.apps.api_registry.models.DeleteKongOnDeleteMixin, models.Model),
        ),
        migrations.AddField(
            model_name='tokenrequest',
            name='state',
            field=models.CharField(choices=[('PENDING', 'Pendiente'), ('ACCEPTED', 'Aceptada'), ('REJECTED', 'Rechazada')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='jwtcredential',
            name='consumer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api_registry.KongConsumer'),
        ),
        migrations.AlterUniqueTogether(
            name='kongconsumer',
            unique_together={('api', 'applicant')},
        ),
    ]
