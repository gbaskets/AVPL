# Generated by Django 5.0.1 on 2024-06-10 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_paymenttransaction_address_paymenttransaction_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businesslimitwallet',
            name='isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='tdslogwallet',
            name='isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='isactive',
            field=models.BooleanField(default=True),
        ),
    ]
