from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from vendor_app.models import *
from main_app.models import *
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from  user_app.models import *


class BusinessMainCategory(models.Model):
	title = models.CharField(max_length=255)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return self.title

class BusinessCategory(models.Model):
	businessmaincategory = models.ForeignKey(BusinessMainCategory, on_delete=models.CASCADE, null=True,blank=True)
	title = models.CharField(max_length=255)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return self.title

class MainSiteUrl(models.Model):
	baseurl = models.CharField(max_length=255)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return self.baseurl
	
class MinAmountForFreeDelivery(models.Model):
	amount = models.FloatField()
	def __str__(self):
		return 'Minimum Amount for Free Delivery is Rs '+str(self.amount)+' (Click Here to Change)'

class CompanyContactUs(models.Model):
	address = models.TextField(null=True,blank=True)
	mobile = models.IntegerField(null=True,blank=True)
	email = models.CharField(max_length=255,null=True,blank=True)
	whatsapp = models.CharField(max_length=255,null=True,blank=True,default="https://www.whatsapp.com/")
	facbook = models.CharField(max_length=255,null=True,blank=True,default="https://www.facebook.com/")
	instagram= models.CharField(max_length=255,null=True,blank=True,default="https://www.instagram.com/")
	twitter = models.CharField(max_length=255,null=True,blank=True,default="https://twitter.com/")
	linkedin = models.CharField(max_length=255,null=True,blank=True,default="https://www.linkedin.com/")
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'CompanyContactUs'

class WalletTransferApprovalSettings(models.Model):
	customer = models.BooleanField(default = True)
	vendor = models.BooleanField(default = True)
	admin = models.BooleanField(default = True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.customer) + ' | ' + str(self.vendor)  + " | " + str(self.admin)  + " | " 


class HomeBanner(models.Model):
	category=models.ForeignKey("inventory_app.ProductCategory",on_delete=models.SET_NULL ,null=True,blank=True)
	title = models.CharField(max_length=255)
	description = models.CharField(max_length=255,null=True,blank=True)
	link = models.CharField(max_length=255,null=True,blank=True )
	image = models.FileField(upload_to='homebanner/image',null=True,blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return self.title

# class DeliveryCharge(models.Model):
# 	amount = models.FloatField()
# 	def __str__(self):
# 		return str(self.amount)



# class Savings(models.Model):
# 	savings = models.FloatField(default=0.00)

# 	def __str__(self):
# 		return 'Rs '+str(self.savings)+'/- Admin Savings'

# class PVPairValue(models.Model):
# 	pairvalue = models.FloatField(default=0.00)
# 	def __str__(self):
# 		return 'PV Pair Value -> '+str(self.pairvalue)

# class PVConversionValue(models.Model):
# 	conversionvalue = models.FloatField(default=0.0)

# 	def __str__(self):
# 		return 'PV Conversion Value -> '+str(self.conversionvalue)

# class Query(models.Model):
# 	user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
# 	query_date = models.DateTimeField(auto_now=True, null=True, blank=True)
# 	anonymous = models.BooleanField(default=False)
# 	name = models.CharField(max_length=100, null=True, blank=True)
# 	email = models.CharField(max_length=100, null=True, blank=True)
# 	mobile = models.CharField(max_length=15, null=True, blank=True)
# 	subject = models.CharField(max_length=255)
# 	message = models.TextField()
# 	image = models.FileField(upload_to='query',null=True,blank=True)
# 	reply = models.TextField(default="No-Reply")
# 	reply_image = models.FileField(upload_to='reply_query',null=True,blank=True)
# 	status = models.IntegerField(default=0)

# 	def __str__(self):
# 		return  self.name

class Tax(models.Model):
	currenttax = models.FloatField(default=0.00)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	
	def __str__(self):
		return 'Current Tax '+str(self.currenttax)

class TDS(models.Model):
	currenttds = models.FloatField(default=0.00)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Current Total TDS '+str(self.currenttds)

class TDSPay(models.Model):
	transactiondate = models.DateTimeField()
	currenttds = models.FloatField(default=0.0)
	tdspaid = models.FloatField(default=0.0)
	tdsremaining = models.FloatField(default=0.0)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return 'TDS Paid Transaction ' +str(self.id) + ' ' +str(self.transactiondate)

class TaxPay(models.Model):
	transactiondate = models.DateTimeField()
	taxcurrent = models.FloatField(default=0.0)
	taxpaid = models.FloatField(default=0.0)
	taxremaining = models.FloatField(default=0.0)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return +str(self.transactiondate)
	

class AboutUs(models.Model):
	title = models.CharField(max_length=255)
	content = RichTextUploadingField(null=True, blank=True)
	image = models.ImageField(upload_to='aboutus/image', null=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.title)

class Blog(models.Model):
	title = models.CharField(max_length=255)
	content = RichTextUploadingField(null=True, blank=True)
	image = models.ImageField(upload_to='blog/image', null=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.title)

class Gallery(models.Model):
	title = models.CharField(max_length=255)
	content = models.TextField(null=True)
	image = models.ImageField(upload_to='gallery/image', null=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)	
	def __str__(self):
		return str(self.title)


# from django.contrib.auth.models import Permission

# class StaffsUser(models.Model):
# 	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staffsuser')
# 	mobile = models.CharField(max_length=10, null=True, blank=True)
# 	address = models.CharField(max_length=100, null=True, blank=True)
# 	zipcode = models.CharField(max_length=20, null=True, blank=True)
# 	gender = models.CharField(max_length=20, null=True, blank=True)
# 	profile_pic =  models.ImageField(upload_to='profile', null=True, blank=True)
# 	department = models.CharField(max_length=100, null=True, blank=True)
# 	designation = models.CharField(max_length=100, null=True, blank=True)
	

# 	def __str__(self):
# 		return str(self.user)
