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
	


class ProductRating(models.Model):
    productvariants = models.ForeignKey(ProductVariants,on_delete=models.CASCADE,blank=True,null=True,related_name="product_variantsimg")
    # order = models.ForeignKey(OrderItems, null=True, blank= True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
    review = models.TextField()
    rating = models.FloatField()
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
    def __str__(self):
        return self.productvariants.productvariantname+' Rating '+str(self.rating)




class Address(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	addresstype = models.CharField(max_length=30,default='Both', choices=(('Billing', 'Billing'), ('Shipping', 'Shipping'),('Both','Both')))
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
	gstno=models.CharField(max_length=255, null=True, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


	def __str__(self):
		return str(self.firstname)+ ' Address'	




class PaymentTransaction(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	paymentgatway=models.CharField(max_length=255)
	transactionid = models.CharField(max_length=255)
	transactionrealted= models.CharField(max_length=255)
	transactiondetails = models.TextField(null=True,blank=True)
	address = models.ForeignKey(Address, on_delete=models.CASCADE,blank=True,null=True)
	amount = models.FloatField(default=0.00)
	status = models.BooleanField(default=False)#use for payment status
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'PaymentTransaction'+str(self.transactionid)
	


class Wallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	admin = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,related_name="admin")
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Wallet of '+ ' ' + str(self.customer) + ' ' +  str(self.vendor)

class WalletTransaction(models.Model):
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
	transactiondate = models.DateTimeField()
	transactiontype = models.CharField(max_length=20)
	transactionamount = models.FloatField()
	transactionrealted= models.CharField(max_length=255,null=True,blank=True)
	transactiondetails = models.TextField(null=True,blank=True)
	transactionid = models.CharField(max_length=255,null=True,blank=True)
	previousamount = models.FloatField()
	remainingamount = models.FloatField()
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Wallet Transaction ID '+str(self.id)


class BusinessLimitWallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'BusinessLimitWallet of '+ ' ' + str(self.customer) + ' ' +  str(self.vendor)

class BusinessLimitWalletTransaction(models.Model):
	businesslimitwallet = models.ForeignKey(BusinessLimitWallet, on_delete=models.CASCADE)
	transactiondate = models.DateTimeField()
	transactiontype = models.CharField(max_length=20)
	transactionrealted= models.CharField(max_length=255,null=True,blank=True)
	transactiondetails = models.TextField(null=True,blank=True)
	transactionid = models.CharField(max_length=255,null=True,blank=True)
	transactionamount = models.FloatField()
	previousamount = models.FloatField()
	remainingamount = models.FloatField()
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Wallet Transaction ID '+str(self.id)



class WithdrawRequest(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	requestdate = models.DateTimeField()
	amount = models.FloatField()
	transactionid = models.CharField(max_length=255,null=True,blank=True)
	creditedamount = models.FloatField(default=0.0)
	tds = models.FloatField(default=0.0)
	isactive = models.PositiveIntegerField(default=0)
	
	def __str__(self):
		return 'Withdraw Request of '+str(self.vendor)


class WithdrawMoneyWallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	admin = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,related_name="withdrawadmin")
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'WithdrawMoneyWallet of '+ ' ' + str(self.customer) + ' ' +  str(self.vendor)
 

class WithdrawMoneyWalletTransaction(models.Model):
	withdrawmoneywallet = models.ForeignKey(WithdrawMoneyWallet, on_delete=models.CASCADE)
	transactiondate = models.DateTimeField()
	transactiontype = models.CharField(max_length=20)
	transactionamount = models.FloatField()
	transactionrealted= models.CharField(max_length=255,null=True,blank=True)
	transactiondetails = models.TextField(null=True,blank=True)
	transactionid = models.CharField(max_length=255,null=True,blank=True)
	previousamount = models.FloatField()
	remainingamount = models.FloatField()
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'WithdrawMoneyWallet Transaction ID '+str(self.id)


# Wallet	
class CommissionWallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	admin = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,related_name="adminuser")
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'Commission Wallet of '+ ' ' + str(self.currentbalance) + ' ' + str(self.customer) + ' ' +  str(self.vendor)
	

# Wallet Transactions
class CommissionWalletTransaction(models.Model):
	commissionwallet = models.ForeignKey(CommissionWallet, on_delete=models.CASCADE)
	transactiondate = models.DateTimeField()
	transactiontype = models.CharField(max_length=20)
	transactionrealted= models.CharField(max_length=255,null=True,blank=True)
	transactiondetails = models.TextField(null=True,blank=True)
	transactionid = models.CharField(max_length=255,null=True,blank=True)
	transactionamount = models.FloatField()
	previousamount = models.FloatField()
	remainingamount = models.FloatField()
	isverified = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.transactiondate)+' Commission Transaction'

class TaxLog(models.Model):
	transactiondate =  models.DateTimeField(null=True)
	salesorderitems = models.ForeignKey('sales_app.SalesOrderItems', on_delete=models.CASCADE, null=True, blank=True)
	taxamount = models.FloatField(default=0.00)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.transactiondate)

class TDSLogWallet(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,blank=True,null=True)
	admin=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,related_name="admintdswallet")
	currentbalance = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return 'TDS_Log_Wallet '+str(self.customer)

class TDSLogWalletTransaction(models.Model):
	tdslogwallet = models.ForeignKey(TDSLogWallet, on_delete=models.CASCADE,null=True,blank=True)
	transactiondate = models.DateTimeField(null=True)
	transactiontype = models.CharField(max_length=255,null=True)
	transactionrealted= models.CharField(max_length=255,null=True,blank=True)
	transactiondetails = models.TextField(null=True,blank=True)
	transactionid = models.CharField(max_length=255,null=True,blank=True)
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
	transactionrealted= models.CharField(max_length=255,null=True,blank=True)
	transactiondetails = models.TextField(null=True,blank=True)
	amount = models.IntegerField(default=0.00)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.sender) + ' | ' + str(self.receiver)








	




















