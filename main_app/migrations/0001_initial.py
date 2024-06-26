# Generated by Django 5.0.1 on 2024-01-15 20:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer_app', '__first__'),
        ('inventory_app', '__first__'),
        ('vendor_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('addresstype', models.CharField(choices=[('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')], default='Home', max_length=30)),
                ('companyname', models.CharField(blank=True, max_length=255, null=True)),
                ('firstname', models.CharField(blank=True, max_length=255, null=True)),
                ('lastname', models.CharField(blank=True, max_length=255, null=True)),
                ('streetaddress', models.CharField(blank=True, max_length=255, null=True)),
                ('nearbyaddress', models.CharField(blank=True, max_length=255, null=True)),
                ('pincode', models.IntegerField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('mobile', models.IntegerField(blank=True, null=True)),
                ('isdefaultaddress', models.BooleanField(default=False)),
                ('isbillingaddress', models.BooleanField(default=False)),
                ('isshippingaddress', models.BooleanField(default=False)),
                ('gstno', models.CharField(blank=True, max_length=255, null=True)),
                ('isactive', models.BooleanField(default=True)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('selfpickup', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('productvariants', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_app.productvariants')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('isread', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('isreadby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='isreadby', to=settings.AUTH_USER_MODEL)),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updatedby', to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentgatway', models.CharField(max_length=255)),
                ('transactionid', models.CharField(max_length=255)),
                ('transactionrealted', models.CharField(max_length=255)),
                ('transactiondetails', models.TextField(blank=True, null=True)),
                ('isverified', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='TDSLogWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currentbalance', models.FloatField(default=0.0)),
                ('isactive', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='TDSLogWalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactiontype', models.CharField(max_length=255, null=True)),
                ('amount', models.FloatField(default=0.0)),
                ('creditedamount', models.FloatField(default=0.0)),
                ('tdsamount', models.FloatField(default=0.0)),
                ('previousamount', models.FloatField(blank=True, null=True)),
                ('remainingamount', models.FloatField(blank=True, null=True)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('tdslogwallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.tdslogwallet')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currentbalance', models.FloatField(default=0.0)),
                ('isactive', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='WalletBalanceTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=255)),
                ('receiver', models.CharField(max_length=255)),
                ('transectionid', models.CharField(max_length=256, unique=True)),
                ('amount', models.IntegerField(default=0.0)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactiondate', models.DateTimeField()),
                ('transactiontype', models.CharField(max_length=20)),
                ('transactionamount', models.FloatField()),
                ('previousamount', models.FloatField()),
                ('remainingamount', models.FloatField()),
                ('isverified', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.wallet')),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('selfpickup', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('customer', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('productvariants', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_app.productvariants')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
    ]
