# Generated by Django 5.0.4 on 2024-05-19 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_app", "0005_homebanner_category_delete_homefooterbanner"),
    ]

    operations = [
        migrations.AddField(
            model_name="homebanner",
            name="isactive",
            field=models.BooleanField(default=True),
        ),
    ]
