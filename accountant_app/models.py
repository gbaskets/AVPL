from django.db import models
from django.contrib.auth.models import User, AbstractUser
# Create your models here.
class AccountTypeGroup(models.Model):
	name  = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return self.name

class AccountType(models.Model):
	accounttypegroup = models.ForeignKey(AccountTypeGroup, on_delete=models.CASCADE, null=True, blank=True,related_name="accounttypegroups")
	name=models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return self.name

class Account(models.Model):
    store = models.ForeignKey("store_app.Store", on_delete = models.CASCADE, null = True, blank = True)
    admin = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True,related_name="admins")
    accounttype = models.ForeignKey(AccountType, on_delete=models.CASCADE, null=True, blank=True)
    accountname = models.CharField(max_length = 255)
    accountcode = models.CharField(max_length = 255, null = True, blank = True)
    openingbalance = models.FloatField(default =0.00)
    transctiontype=models.CharField(max_length = 255, null = True, blank = True)
    streetaddress = models.CharField(max_length=255, null=True, blank=True)
    nearbyaddress = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    city=models.CharField(max_length=255, null=True, blank=True)
    state=models.CharField(max_length=255, null=True, blank=True)
    country=models.CharField(max_length=255, null=True, blank=True)
    pancardno=models.CharField(max_length=10, null=True, blank=True)
    pancarddoc = models.FileField(upload_to='store/pancarddoc',null=True, blank=True)
    gstno=models.CharField(max_length=50, null=True, blank=True)
    gstnodoc = models.FileField(upload_to='store/gstnodoc',null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
  
    def __str__(self):

        return self.accountname + " " + str(self.id)


# class MannualJournal(models.Model):
# 	store = models.ForeignKey(Store, on_delete = models.CASCADE,null = True, blank = True)
# 	payment_receive = models.IntegerField( null=True, blank=True)
# 	billpayment = models.IntegerField( null=True, blank=True)

# 	invoiceid  = models.IntegerField( blank = True, null = True)
# 	purshaseinvoiceid  = models.IntegerField(blank = True, null = True)

# 	createdby   = models.ForeignKey(User,on_delete = models.CASCADE, blank = True, null = True)
# 	createddate = models.DateField(null = True, blank = True)
# 	referenceno = models.CharField(max_length = 255, null = True, blank = True)
# 	status       = models.BooleanField(default = False)
# 	totalcredit = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00, null = True, blank = True)
# 	totaldebit  = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00, null =True, blank = True)
# 	amount       = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
# 	journaltype=models.CharField(max_length = 100, null = True, blank = True)
	
# 	def __str__(self):
# 		return str(self.id) + ' ' +str(self.store.store_name)




# class AccountEntry(models.Model):
# 	account         = models.ForeignKey(Account, on_delete = models.CASCADE, null = True, blank = True)
# 	expense_id      = models.IntegerField(null = True, blank = True) #use expense_id to store, id of expense model.
# 	store_id        = models.IntegerField(null = True, blank = True) #use store_id to store, id of store model.
# 	date            = models.DateTimeField(auto_now= True)
# 	transaction_user=models.CharField(max_length = 100,null = True, blank = True)
# 	entrytype      = models.CharField(max_length = 50)
# 	title           = models.CharField(max_length = 255, default ='No-Title')
# 	ismatched      = models.BooleanField(default=False)
# 	amount          = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
# 	balance         = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00,null = True, blank = True)
# 	totalcredit    = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00,null = True, blank = True)
# 	totaldebit     = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00,null = True, blank = True)
# 	attechfile     = models.FileField(upload_to ='ledger_file', null = True, blank = True)
# 	description     = models.TextField(null = True, blank = True)
 
# 	def __str__(self):
# 		return str(self.id)













# class DefaultAccount(models.Model):
# 	openingdate = models.DateTimeField(auto_now_add = True)
# 	updateddate = models.DateTimeField(auto_now = True)
# 	accountname = models.CharField(max_length = 255)
# 	accounttype = models.CharField(max_length = 255, null = True, blank = True)
# 	accounttypechangeable = models.BooleanField(default = False)
# 	accountcode = models.CharField(max_length = 100, null = True, blank = True)
# 	description  = models.CharField(max_length = 255, null = True, blank = True)
# 	currentbalance = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00,null = True, blank=True)

# 	def __str__(self):
# 		return self.accountname






# class SubAccount(models.Model):
#     defaultaccount = models.ForeignKey(DefaultAccount, on_delete=models.CASCADE, null=True, blank=True)
#     account_name    = models.CharField(max_length = 255)
#     def __str__(self):
#         return self.account_name


# class SubAccountEntry(models.Model):
#     subaccount  = models.ForeignKey(SubAccount,on_delete=models.CASCADE,null=True,blank=True)
#     expenseid   = models.IntegerField(null=True, blank=True) #use expense_id to store, id of expense model.
#     storeid     = models.IntegerField(null=True, blank=True) #use store_id to store, id of store model.
#     entrytype   = models.CharField(max_length=50)
#     balance 	 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,blank=True)
#     totalcredit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,blank=True)
#     totaldebit  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,blank=True)
    
#     def __str__(self):
#         return str(self.id)



# class Bank_or_Credit_Card(models.Model):
# 	Select_Account_Type=(
# 		('Bank','Bank'),
# 		('Credit_Card','Credit_Card'),)
# 	bank_name    = models.CharField(max_length=255, null = True, blank = True)
# 	account_type = models.CharField(max_length=55,choices=Select_Account_Type,default='Bank')
# 	logo         = models.ImageField(upload_to="bank/logo",null = True, blank = True)
# 	is_active =  models.BooleanField(default=True)
# 	def __str__(self):
# 		return str(self.bank_name) + ':' +str(self.account_type)




# class Store_Bank_or_Credit_Card(models.Model):
# 	bank_or_credit_card = models.ForeignKey(Bank_or_Credit_Card, on_delete = models.CASCADE,null = True, blank = True)
# 	store               = models.ForeignKey(Store, on_delete = models.CASCADE,null = True, blank = True)
# 	account_name        = models.CharField(max_length=255, null = True, blank = True)
# 	account_code        = models.CharField(max_length=255, null = True, blank = True)
# 	currency            = models.CharField(max_length=255, null = True, blank = True)
# 	account_number      = models.CharField(max_length=255, null = True, blank = True)
# 	ifse                = models.CharField(max_length=255, null = True, blank = True)
# 	description         = models.TextField(null=True,blank=True)
# 	is_active           = models.BooleanField(default=True)



# 	def __str__(self):
# 		return str(self.account_name) + ':' +str(self.store)


# class Store_Bank_Statement_Entry(models.Model):
# 	store = models.ForeignKey(Store, on_delete = models.CASCADE,null = True, blank = True)
# 	store_bank_or_credit_card 	= models.ForeignKey(Store_Bank_or_Credit_Card, on_delete = models.CASCADE,null = True, blank = True)
# 	created_date            	= models.DateTimeField(auto_now_add = True)
# 	date            			= models.DateField(null=True,blank=True)
# 	description					= models.TextField(null=True,blank=True)
# 	ref_no      				= models.TextField(null = True, blank = True)
# 	value_date  				= models.DateField(null=True,blank=True)
# 	is_matched      			= models.BooleanField(default=False)
# 	withdrawal_amount      		= models.FloatField(null=True,blank=True)
# 	deposit_amount      		= models.FloatField(null=True,blank=True)
# 	closing_balance         	= models.FloatField(null=True,blank=True)

# 	def __str__(self):
# 		return str(self.id)







