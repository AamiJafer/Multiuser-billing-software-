# Generated by Django 5.0 on 2024-02-14 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0011_remove_creditnote_salesinvoice_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditnoteitem',
            name='item',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
