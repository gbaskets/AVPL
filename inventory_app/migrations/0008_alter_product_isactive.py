# Generated by Django 5.0.4 on 2024-05-05 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory_app", "0007_alter_productvariants_isactive"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="isactive",
            field=models.BooleanField(default=False),
        ),
    ]