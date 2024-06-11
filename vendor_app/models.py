from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey
from admin_app.models import *
from main_app.models import *
from .models import *
from store_app.models import *
import datetime
from ckeditor.fields import RichTextField

# # # Per Product Commission 

class Vendor(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='Vendor')
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
	profilepic =  models.ImageField(upload_to='vendor/profile_pic', null=True, blank=True)

	#Personal User PV
	idproof=models.CharField(max_length=255, null=True, blank=True)
	idno=models.CharField(max_length=255, null=True, blank=True)
	frontidproofdoc = models.FileField(upload_to='vendor/frontidproofdoc',null=True, blank=True)
	backidproofdoc= models.FileField(upload_to='vendor/backidproofdoc',null=True, blank=True)
	addressproof=models.CharField(max_length=255, null=True, blank=True)
	addressno=models.CharField(max_length=255, null=True, blank=True)
	frontaddressproofdoc = models.FileField(upload_to='vendor/frontaddressproofdoc',null=True, blank=True)
	backddressproofdoc = models.FileField(upload_to='vendor/backddressproofdoc',null=True, blank=True)
	pancardno=models.CharField(max_length=10, null=True, blank=True)
	pancarddoc = models.FileField(upload_to='vendor/pancarddoc',null=True, blank=True)
	gstno=models.CharField(max_length=50, null=True, blank=True)
	gstnodoc = models.FileField(upload_to='vendor/gstnodoc',null=True, blank=True)
	
	bankname = models.CharField(max_length=255,null=True, blank=True)
	bankifsc = models.CharField(max_length=255,null=True, blank=True)
	bankholder = models.CharField(max_length=255,null=True, blank=True)
	bankaccountno= models.IntegerField(null=True, blank=True)
	bankdoc = models.FileField(upload_to='vendor/bankdoc',null=True, blank=True)

	pv = models.FloatField(default=0.0)
	sponsor = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
	subscribed = models.BooleanField(default=False)

	storecreated = models.BooleanField(default=False)
	verified = models.BooleanField(default=False)
	docsubmitted = models.BooleanField(default=False,null=True, blank=True)
	isavplvendor = models.BooleanField(default=False,null=True, blank=True)
	createdat = models.DateTimeField(auto_now_add=True,null=True, blank=True)
	updatedon = models.DateTimeField(auto_now=True,null=True, blank=True)

	
	def __str__(self):
		return str(self.user) +' :'+ str(self.firstname)





# #model for user subscription request
# class UserSubscriptionRequest(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
# 	month = models.PositiveIntegerField(default=1)
# 	amount = models.FloatField(default=0.0)
# 	is_active = models.BooleanField(default=False)
# 	class Meta:
# 		db_table = "UserSubscriptionRequest"
# 	def __str__(self):
# 		return str(self.user.usr.first_name)+ ' ' +str(self.vendor.first_name)


	
# ######################################################################################################################################

