# Generated by Django 5.0.1 on 2024-04-24 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_commissionwallet_commissionwallettransaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commissionwallettransaction',
            name='commissionwallet',
        ),
        migrations.RemoveField(
            model_name='commissionwallettransaction',
            name='updatedby',
        ),
        migrations.DeleteModel(
            name='CommissionWallet',
        ),
        migrations.DeleteModel(
            name='CommissionWalletTransaction',
        ),
    ]