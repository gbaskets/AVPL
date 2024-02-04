# from ast import Store
# from django.db import models

# # Create your models here.
# from django.db import models
# from django.contrib.auth.models import User, AbstractUser
# from django.db.models.fields import DateTimeField
# from vendor_app.models import *
# from main_app.models import *




# class PaymentInfo(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payinfo')
# 	account_no = models.CharField(max_length=50)
# 	bank_name = models.CharField(max_length=50)
# 	ifsc = models.CharField(max_length=50)
# 	pan = models.ImageField(upload_to='payment',null=True, blank=True)
# 	aadhar = models.ImageField(upload_to='payment',null=True, blank=True)
# 	class Meta:
# 		db_table="PaymentInfo"
# 	def __str__(self):
# 		return 'Payment Info of '+str(self.user)

# class UserWithdrawRequest(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdraw_request')
# 	request_date = models.DateTimeField()
# 	amount = models.FloatField()
# 	credited_amount = models.FloatField(default=0.0)
# 	tds = models.FloatField(default=0.0)
# 	is_active = models.PositiveIntegerField(default=0)
# 	class Meta:
# 		db_table="UserWithdrawRequest"
# 	def __str__(self):
# 		return 'Withdraw Request of '+str(self.user)

# class CreditedMoney(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	current_balance = models.FloatField(default=0.0)

# 	def __str__(self):
# 		return 'CreditedMoney '+str(self.user)

# class CreditedMoneyTransaction(models.Model):
# 	creditedmoney = models.ForeignKey(CreditedMoney, on_delete=models.CASCADE)
# 	transaction_date = models.DateTimeField()
# 	transaction_type = models.CharField(max_length=20)
# 	transaction_amount = models.FloatField()
# 	previous_amount = models.FloatField()
# 	remaining_amount = models.FloatField()
	
# 	def __str__(self):
# 		return 'CreditedMoney Transaction ID '+str(self.id)




# #showing User Vendor Relation
# class UserVendorRelation(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	vendor = models.OneToOneField(Vendor,on_delete=models.CASCADE,primary_key=True,)
# 	class Meta:
# 		db_table="UserVendorRelation"
# 	def __str__(self):
# 		return self.vendor.first_name+' is related '+self.user.usr.first_name

# class Membership(models.Model):
# 	user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True, related_name="member")
# 	subscribed_on = DateTimeField(auto_now=True)
# 	class Meta:
# 		db_table="Membership"
# 	def __str__(self):
# 		return self.user.usr.first_name
# #bellow fn holds subscription payment details
# class Memberip_Receipt(models.Model):
# 	receipt_date = models.DateTimeField(auto_now=True)
# 	user = models.ForeignKey(User,on_delete=models.CASCADE)
# 	razorpay_order_id = models.CharField(max_length=100)
# 	payment_id = models.CharField(max_length=200, null=True, blank=True)
# 	amount = models.FloatField()
# 	is_active = models.BooleanField(default=False)
# 	class Meta:
# 			db_table ="Memberip_Receipt"
# 	def __str__(self):
# 			return "Receipt ID "+str(self.id)

# # to calculate year
# class UserSubscription(models.Model):
# 	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscribed_usr')
# 	subscrbe_on = models.DateTimeField(auto_now=True)
# 	months = models.PositiveIntegerField(default=1)
# 	class Meta:
# 		db_table= "UserSubscription"
# 	def __str__(self):
# 		return str(self.user)

# class Billing_Request(models.Model):
# 	created_on = models.DateTimeField(auto_now_add=True)
# 	updated_on = models.DateTimeField(auto_now=True)
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	store = models.ForeignKey(Store, on_delete=models.CASCADE)
# 	amount = models.FloatField(default=0.0)
# 	plan = models.CharField(max_length=100, default="Level")
# 	is_active = models.BooleanField(default=False)
# 	class Meta:
# 		db_table= "Billing_Request"
# 	def __str__(self):
# 		return str(self.user)