# Generated by Django 5.0.1 on 2024-08-04 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0021_alter_product_isactive_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='isactive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='productvariants',
            name='isactive',
            field=models.BooleanField(default=False),
        ),
    ]
