# Generated by Django 5.0.1 on 2024-07-17 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_app', '0006_salesorder_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorderitems',
            name='admincommission',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]