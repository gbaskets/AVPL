# Generated by Django 5.0.1 on 2024-07-17 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_app', '0007_salesorderitems_admincommission'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='totaladmincommission',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
