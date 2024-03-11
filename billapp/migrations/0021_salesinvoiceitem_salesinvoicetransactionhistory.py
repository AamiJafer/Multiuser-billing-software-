# Generated by Django 5.0 on 2024-03-11 11:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0020_alter_salesinvoice_party'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesInvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hsn', models.IntegerField(blank=True, default=0, null=True)),
                ('quantity', models.IntegerField(blank=True, default=0, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('tax', models.CharField(blank=True, max_length=255, null=True)),
                ('totalamount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=20, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.company')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.employee')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.item')),
                ('salesinvoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.salesinvoice')),
            ],
        ),
        migrations.CreateModel(
            name='SalesInvoiceTransactionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, null=True)),
                ('action', models.CharField(max_length=255)),
                ('done_by_name', models.CharField(max_length=255)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.company')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.employee')),
                ('salesinvoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.salesinvoice')),
            ],
        ),
    ]
