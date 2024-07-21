# Generated by Django 5.0.1 on 2024-07-21 18:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountant_app', '0001_initial'),
        ('customer_app', '0001_initial'),
        ('store_app', '0003_store_isbestseller'),
        ('vendor_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttype',
            name='accounttypegroup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accounttypegroups', to='accountant_app.accounttypegroup'),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountname', models.CharField(max_length=255)),
                ('accountcode', models.CharField(blank=True, max_length=255, null=True)),
                ('openingbalance', models.FloatField(default=0.0)),
                ('transctiontype', models.CharField(blank=True, max_length=255, null=True)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('accounttype', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accountant_app.accounttype')),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admins', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store_app.store')),
                ('updatedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor_app.vendor')),
            ],
        ),
    ]