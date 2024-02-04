# Generated by Django 5.0.1 on 2024-01-15 20:21

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admin_app', '__first__'),
        ('vendor_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storename', models.CharField(blank=True, max_length=250, null=True, unique=True)),
                ('description', models.CharField(blank=True, max_length=300, null=True)),
                ('registrationno', models.CharField(blank=True, max_length=255, null=True)),
                ('registrationqrcode', models.ImageField(blank=True, null=True, upload_to='store/qrcode')),
                ('streetaddress', models.CharField(blank=True, max_length=255, null=True)),
                ('nearbyaddress', models.CharField(blank=True, max_length=255, null=True)),
                ('pincode', models.IntegerField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='store/logo')),
                ('banner', models.ImageField(blank=True, null=True, upload_to='store/banner')),
                ('msmeno', models.CharField(blank=True, max_length=255, null=True)),
                ('msmedoc', models.FileField(blank=True, null=True, upload_to='store/msmedoc')),
                ('pancardno', models.CharField(blank=True, max_length=10, null=True)),
                ('pancarddoc', models.FileField(blank=True, null=True, upload_to='store/pancarddoc')),
                ('gstno', models.CharField(blank=True, max_length=50, null=True)),
                ('gstnodoc', models.FileField(blank=True, null=True, upload_to='store/gstnodoc')),
                ('shippingpolicy', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('replacementpolicy', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('returnandrefundpolicy', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('createdat', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('isactive', models.BooleanField(default=True)),
                ('businesscategory', models.ManyToManyField(blank=True, to='admin_app.businesscategory')),
                ('businessmaincategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BusinessMainCategory', to='admin_app.businessmaincategory')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Vendor', to='vendor_app.vendor')),
            ],
        ),
    ]
