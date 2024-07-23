# Generated by Django 5.0.1 on 2024-07-24 02:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountant_app', '0009_manualjournalvoucher_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountentry',
            name='manualjournalvoucher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manualjournalvouchers', to='accountant_app.manualjournalvoucher'),
        ),
    ]
