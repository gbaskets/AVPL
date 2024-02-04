from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from store_app.models import Store



class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='User')
    store=models.ForeignKey(Store, on_delete=models.CASCADE, null=True,blank=True)
    mobile = models.IntegerField( null=True, blank=True)
    firstname=models.CharField(max_length=255,null=True,blank=True)
    lastname=models.CharField(max_length=255,null=True,blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    dob=models.DateField(null=True,blank=True)
    streetaddress = models.CharField(max_length=255, null=True, blank=True)
    nearbyaddress = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    city=models.CharField(max_length=255, null=True, blank=True)
    state=models.CharField(max_length=255, null=True, blank=True)
    country=models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    profilepic =  models.ImageField(upload_to='customer/profile_pic', null=True, blank=True)

    #Personal User PV
    idproof=models.CharField(max_length=255, null=True, blank=True)
    idno=models.CharField(max_length=255, null=True, blank=True)
    frontidproofdoc = models.FileField(upload_to='customer/frontidproofdoc',null=True, blank=True)
    backidproofdoc= models.FileField(upload_to='customer/backidproofdoc',null=True, blank=True)
    addressproof=models.CharField(max_length=255, null=True, blank=True)
    addressno=models.CharField(max_length=255, null=True, blank=True)
    frontaddressproofdoc = models.FileField(upload_to='customer/frontaddressproofdoc',null=True, blank=True)
    backddressproofdoc = models.FileField(upload_to='customer/backddressproofdoc',null=True, blank=True)
    pancardno=models.CharField(max_length=10, null=True, blank=True)
    pancarddoc = models.FileField(upload_to='customer/pancarddoc',null=True, blank=True)
    gstno=models.CharField(max_length=50, null=True, blank=True)
    gstnodoc = models.FileField(upload_to='customer/gstnodoc',null=True, blank=True)

    bankname = models.CharField(max_length=255,null=True, blank=True)
    bankifsc = models.CharField(max_length=255,null=True, blank=True)
    bankholder = models.CharField(max_length=255,null=True, blank=True)
    bankaccountno= models.IntegerField(null=True, blank=True)
    bankdoc = models.FileField(upload_to='vendor/bankdoc',null=True, blank=True)

    pv = models.FloatField(default=0.0)
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    isactive = models.BooleanField(default=True)
    subscribed = models.BooleanField(default=False)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + ' ' + str(self.mobile)

