# Generated by Django 5.0.1 on 2024-06-10 18:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0012_alter_address_addresstype'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttransaction',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.address'),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
