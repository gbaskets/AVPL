# Generated by Django 5.0.1 on 2024-07-26 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountant_app', '0012_accounttransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttransaction',
            name='previousprtransactiontype',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
