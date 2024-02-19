# Generated by Django 5.0 on 2024-02-19 06:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0014_creditnote_partystatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditnoteitem',
            name='items',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.item'),
        ),
    ]
