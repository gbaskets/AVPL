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

# # class Vendor_Wallet_Commission(models.Model):
# # 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# # 	current_balance = models.FloatField(default=0.0)
# # 	is_active = models.BooleanField(default=False)
	
# # 	def __str__(self):
# # 		return 'Wallet of '+self.user.email

# # class VendorWalletTransaction(models.Model):
# # 	vendor_wallet_commission = models.ForeignKey(Vendor_Wallet_Commission, on_delete=models.CASCADE)
# # 	transaction_date = models.DateTimeField()
# # 	transaction_type = models.CharField(max_length=20)
# # 	transaction_amount = models.FloatField()
# # 	user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank= True)
# # 	previous_amount = models.FloatField()
# # 	remaining_amount = models.FloatField()
	
# 	# def __str__(self):
# 	# 	return 'Wallet Transaction ID '+str(self.id)

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

# class VendorWithdrawRequest(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_withdraw_request')
# 	request_date = models.DateTimeField()
# 	amount = models.FloatField()
# 	is_active = models.PositiveIntegerField(default=0)
# 	class Meta:
# 		db_table="VendorWithdrawRequest"
# 	def __str__(self):
# 		return 'Withdraw Request of '+str(self.user)


# #Model For Business Limit Model
# class BusinessLimit(models.Model):
# 	vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='business_limit')
# 	current_balance = models.FloatField(default=0.0)
# 	class Meta:
# 		db_table="BusinessLimit"
# 	def __str__(self):
# 		return 'BusinessLimit '+str(self.vendor)

# class Recharge_Receipt(models.Model):
# 	receipt_date = models.DateTimeField(auto_now=True)
# 	vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
# 	razorpay_order_id = models.CharField(max_length=100)
# 	payment_id = models.CharField(max_length=200, null=True, blank=True)
# 	amount = models.FloatField()
# 	is_active = models.BooleanField(default=False)
# 	class Meta:
# 			db_table ="Recharge_Receipt"
# 	def __str__(self):
# 			return "Receipt ID "+str(self.id)

# #Model for Admin commision amount from Business limit(like wallet) to Admin wallet in case COD 
# class BusinessLimitTransaction(models.Model):
# 	business_limit=models.ForeignKey(BusinessLimit,on_delete=models.CASCADE)
# 	receipt=models.ForeignKey(Recharge_Receipt,on_delete=models.CASCADE, null=True, blank=True)
# 	transaction_date = models.DateTimeField()
# 	transaction_name = models.CharField(max_length=100)
# 	transaction_type = models.CharField(max_length=20, choices=(('CREDIT', 'CREDIT'), ('DEBIT', 'DEBIT')))
# 	transaction_amount = models.FloatField()
# 	previous_amount = models.FloatField()
# 	remaining_amount = models.FloatField()
# 	class Meta:
# 			db_table ="BusinessLimitTransaction"
# 	def __str__(self):
# 			return "BusinessLimitTransaction "+str(self.business_limit)

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

