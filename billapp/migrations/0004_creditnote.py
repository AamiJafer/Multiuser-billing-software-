# Generated by Django 5.0 on 2024-01-25 18:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0003_item_itemtransactions_itemtransactionshistory_party_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('returndate', models.DateField()),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.itemtransactions')),
                ('party', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.party')),
                ('salesinvoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.salesinvoice')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
