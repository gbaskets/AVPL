# Generated by Django 5.0.4 on 2024-05-19 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("admin_app", "0006_homebanner_isactive"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homebanner",
            name="subtitle",
        ),
    ]
