# Create your models here.
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from customer_app.models import *
from inventory_app.models import *
from inventory_app.models import ProductVariants
from user_app.models import *
from vendor_app.models import Vendor
from ckeditor.fields import RichTextField


class UserOTP(models.Model):
	mobile=models.IntegerField(null=True,blank=True)
	email=models.EmailField(null=True,blank=True)
	typeuser=models.CharField(max_length=255,null=True,blank=True)
	otp=models.IntegerField()


class Cart(models.Model):
	customer = models.OneToOneField(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.OneToOneField('vendor_app.Vendor', on_delete=models.CASCADE, blank=True,null=True)
	productvariants = models.ForeignKey(ProductVariants, on_delete=models.CASCADE,blank=True,null=True)
	quantity = models.PositiveIntegerField()
	selfpickup = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	
	def __int__(self):
		return self.id

class Wishlist(models.Model):
	customer = models.OneToOneField(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.OneToOneField('vendor_app.Vendor', on_delete=models.CASCADE, blank=True,null=True)
	productvariants = models.ForeignKey(ProductVariants, on_delete=models.CASCADE,blank=True,null=True)
	quantity = models.PositiveIntegerField()
	selfpickup = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	
	def __int__(self):
		return self.id
	


class Address(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	addresstype = models.CharField(max_length=30,default='Home', choices=(('Home', 'Home'), ('Work', 'Work'),('Other','Other')))
	companyname=models.CharField(max_length=255,null=True,blank=True)
	firstname = models.CharField(max_length=255,blank=True,null=True)
	lastname = models.CharField(max_length=255,blank=True,null=True)
	streetaddress = models.CharField(max_length=255, null=True, blank=True)
	nearbyaddress = models.CharField(max_length=255, null=True, blank=True)
	pincode = models.IntegerField(null=True, blank=True)
	city=models.CharField(max_length=255, null=True, blank=True)
	state=models.CharField(max_length=255, null=True, blank=True)
	country=models.CharField(max_length=255, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	mobile = models.IntegerField(null=True, blank=True)
	isdefaultaddress = models.BooleanField(default=False)
	isbillingaddress=models.BooleanField(default=False)
	isshippingaddress=models.BooleanField(default=False)
	gstno=models.CharField(max_length=255, null=True, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


	def __str__(self):
		return self.firstname+' Address'	




class PaymentTransaction(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	paymentgatway=models.CharField(max_length=255)
	transactionid = models.CharField(max_length=255)
	transactionrealted= models.CharField(max_length=255)
	transactiondetails = models.TextField(null=True,blank=True)
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'PaymentTransaction'+str(self.transactionid)
	

class Wallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Wallet of '+ self.customer +  self.vendor

class WalletTransaction(models.Model):
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
	transactiondate = models.DateTimeField()
	transactiontype = models.CharField(max_length=20)
	transactionamount = models.FloatField()
	previousamount = models.FloatField()
	remainingamount = models.FloatField()
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Wallet Transaction ID '+str(self.id)


class TDSLogWallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'TDS_Log_Wallet '+str(self.customer)

class TDSLogWalletTransaction(models.Model):
	tdslogwallet = models.ForeignKey(TDSLogWallet, on_delete=models.CASCADE,null=True,blank=True)
	transactiontype = models.CharField(max_length=255,null=True)
	amount = models.FloatField(default=0.00)
	creditedamount= models.FloatField(default=0.00)
	tdsamount = models.FloatField(default=0.00)
	previousamount = models.FloatField(null=True,blank=True)
	remainingamount = models.FloatField(null=True,blank=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return  'TDS_Log_Wallet Transaction ID '+str(self.id)  + ' ' +str(self.tdslogwallet) + ' ' + str(self.createdat)

class Notification(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	admin = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
	subject = models.CharField(max_length=255)
	message = models.TextField()
	isread = models.BooleanField(default=False)
	isreadby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="isreadby")
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="updatedby")

	def __str__(self):
		return 'Notification '+self.message

class WalletBalanceTransfer(models.Model):
	sender = models.CharField(max_length=255)
	receiver = models.CharField(max_length=255)
	transectionid = models.CharField(max_length=256,unique=True)
	amount = models.IntegerField(default=0.00)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.sender) + ' | ' + str(self.receiver)








	





















