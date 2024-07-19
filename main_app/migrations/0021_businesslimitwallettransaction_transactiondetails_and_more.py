# Generated by Django 5.0.1 on 2024-07-18 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0020_wallettransaction_transactionrealted'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesslimitwallettransaction',
            name='transactiondetails',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businesslimitwallettransaction',
            name='transactionid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='businesslimitwallettransaction',
            name='transactionrealted',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='commissionwallettransaction',
            name='transactiondetails',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='commissionwallettransaction',
            name='transactionid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='commissionwallettransaction',
            name='transactionrealted',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tdslogwallettransaction',
            name='transactiondetails',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tdslogwallettransaction',
            name='transactionid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tdslogwallettransaction',
            name='transactionrealted',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='walletbalancetransfer',
            name='transactiondetails',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='walletbalancetransfer',
            name='transactionrealted',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='transactionid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]