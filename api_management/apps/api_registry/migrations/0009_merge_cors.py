from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [

        ('api_registry', '0008_auto_20180608_1345'),
        ('api_registry', '0007_auto_20180611_1110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kongplugincors',
            old_name='apidata',
            new_name='parent',
        ),
        migrations.RenameModel(
            old_name='kongplugincors',
            new_name='kongapiplugincors',
        ),
    ]
