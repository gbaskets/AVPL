from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from vendor_app.models import *
from main_app.models import *
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField


class Store(models.Model):
	businessmaincategory =models.ForeignKey("admin_app.BusinessMainCategory", on_delete=models.CASCADE,null=True,blank=True,related_name='BusinessMainCategory')
	businesscategory =models.ManyToManyField("admin_app.BusinessCategory",blank=True)
	vendor = models.ForeignKey("vendor_app.Vendor", on_delete=models.CASCADE,null=True,blank=True,related_name='Vendor')
	storename = models.CharField(max_length=250,unique=True,null=True,blank=True)
	description = models.CharField(max_length=300,null=True,blank=True)
	closingday = models.CharField(max_length=300,null=True,blank=True)
	closingtime = models.TimeField(max_length=300,null=True,blank=True)
	openingtime = models.TimeField(max_length=300,null=True,blank=True)
	registrationno= models.CharField(max_length=255,null=True,blank=True)  
	registrationqrcode= models.ImageField(upload_to='store/qrcode',null=True, blank=True)
	streetaddress = models.CharField(max_length=255, null=True, blank=True)
	nearbyaddress = models.CharField(max_length=255, null=True, blank=True)
 
	pincode = models.IntegerField(null=True, blank=True)
	city=models.CharField(max_length=255, null=True, blank=True)
	state=models.CharField(max_length=255, null=True, blank=True)
	country=models.CharField(max_length=255, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	logo = models.ImageField(upload_to='store/logo',null=True, blank=True)
	banner = models.ImageField(upload_to='store/banner',null=True, blank=True)

	#Doc
	storeregistrationtype=models.CharField(max_length=255, null=True, blank=True)
	msmeno=models.CharField(max_length=255, null=True, blank=True)
	msmedoc = models.FileField(upload_to='store/msmedoc',null=True, blank=True)
	pancardno=models.CharField(max_length=10, null=True, blank=True)
	pancarddoc = models.FileField(upload_to='store/pancarddoc',null=True, blank=True)
	gstno=models.CharField(max_length=50, null=True, blank=True)
	gstnodoc = models.FileField(upload_to='store/gstnodoc',null=True, blank=True)

	#policy
	shippingpolicy = RichTextField(null=True, blank=True)
	replacementpolicy = RichTextField(null=True, blank=True)
	returnandrefundpolicy = RichTextField(null=True, blank=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	isbestseller = models.BooleanField(default=False)
	isactive = models.BooleanField(default=True)

	def __str__(self):
		return str(self.storename)


