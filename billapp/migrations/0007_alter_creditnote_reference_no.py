# Generated by Django 5.0 on 2024-02-09 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0006_alter_creditnote_reference_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditnote',
            name='reference_no',
            field=models.IntegerField(default='0', null=True),
        ),
    ]
