# Generated by Django 5.0.1 on 2024-08-04 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0007_remove_store_isselectedcurrentstore'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='isselectedcurrentstore',
            field=models.BooleanField(default=False),
        ),
    ]