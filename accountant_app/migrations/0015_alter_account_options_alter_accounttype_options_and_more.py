# Generated by Django 5.0.1 on 2024-08-04 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accountant_app', '0014_remove_account_accounttype_accounttypelist_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'verbose_name': 'Account Ledger'},
        ),
        migrations.AlterModelOptions(
            name='accounttype',
            options={'verbose_name': 'Account Group'},
        ),
        migrations.AlterModelOptions(
            name='accounttypegroup',
            options={'verbose_name': 'Nature of Account'},
        ),
        migrations.AlterModelOptions(
            name='accounttypelist',
            options={'verbose_name': 'Account Sub-Group'},
        ),
    ]
