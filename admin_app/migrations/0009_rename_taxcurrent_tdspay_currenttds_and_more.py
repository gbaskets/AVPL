# Generated by Django 5.0.1 on 2024-07-09 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0008_tax_taxpay_tds_tdspay'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tdspay',
            old_name='taxcurrent',
            new_name='currenttds',
        ),
        migrations.RenameField(
            model_name='tdspay',
            old_name='taxpaid',
            new_name='tdspaid',
        ),
        migrations.RenameField(
            model_name='tdspay',
            old_name='taxremaining',
            new_name='tdsremaining',
        ),
    ]
