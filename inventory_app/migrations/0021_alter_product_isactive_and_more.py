# Generated by Django 5.0.1 on 2024-08-04 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0020_product_ispublished_productvariants_ispublished'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='productvariants',
            name='isactive',
            field=models.BooleanField(default=True),
        ),
    ]
