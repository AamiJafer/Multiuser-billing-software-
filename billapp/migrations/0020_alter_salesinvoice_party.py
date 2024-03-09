# Generated by Django 5.0 on 2024-03-08 18:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0019_remove_creditnote_reference_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesinvoice',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.party'),
        ),
    ]
