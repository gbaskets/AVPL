# Generated by Django 5.0.1 on 2024-01-15 20:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer_app', '0001_initial'),
        ('inventory_app', '0001_initial'),
        ('main_app', '0001_initial'),
        ('store_app', '0001_initial'),
        ('vendor_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderno', models.CharField(blank=True, max_length=250, null=True)),
                ('shippingcharges', models.FloatField(blank=True, default=0.0, null=True)),
                ('subtotal', models.FloatField(blank=True, default=0.0, null=True)),
                ('tax', models.FloatField(blank=True, default=0.0, null=True)),
                ('total', models.FloatField(blank=True, default=0.0, null=True)),
                ('pv', models.FloatField(default=0.0)),
                ('selfpickup', models.BooleanField(default=False)),
                ('ispaymentpaid', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.address')),
                ('customer', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('paymenttransaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.paymenttransaction')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='SalesOrderItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.FloatField(blank=True, default=0.0, null=True)),
                ('subtotal', models.FloatField(blank=True, default=0.0, null=True)),
                ('tax', models.FloatField(blank=True, default=0.0, null=True)),
                ('total', models.FloatField(blank=True, default=0.0, null=True)),
                ('orderstatus', models.CharField(blank=True, default='Pending', max_length=255, null=True)),
                ('deliveryexpected', models.DateField(blank=True, null=True)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('cancellationreason', models.CharField(blank=True, max_length=500, null=True)),
                ('cancelledon', models.DateTimeField(blank=True, null=True)),
                ('productvariants', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_app.productvariants')),
                ('salesorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales_app.salesorder')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store_app.store')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
