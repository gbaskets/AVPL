from django.db import models
from django.contrib.auth.models import User, AbstractUser
# Create your models here.

class AccountTypeGroup(models.Model):
    name  = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        verbose_name = 'Nature of Account'
    def __str__(self):
        return self.name

        
class AccountType(models.Model):
    accounttypegroup = models.ForeignKey(AccountTypeGroup, on_delete=models.CASCADE, null=True, blank=True,related_name="accounttypegroups")
    name=models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        verbose_name = 'Account Group'

    def __str__(self):
        return f'{self.name} > {self.accounttypegroup}' 

class AccountTypeList(models.Model):
    accounttype = models.ForeignKey(AccountType, on_delete=models.CASCADE, null=True, blank=True,related_name="accounttypes")
    name=models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        verbose_name = 'Account Sub-Group'

    def __str__(self):
         return f'{self.name} > {self.accounttype}'       

class Account(models.Model):
    store = models.ForeignKey("store_app.Store", on_delete = models.CASCADE, null = True, blank = True)
    admin = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True,related_name="admins")
    accounttypelist = models.ForeignKey(AccountTypeList, on_delete=models.CASCADE, null=True, blank=True,related_name="accounttypelists")
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
    
    class Meta:
        verbose_name = 'Account Ledger'

    def __str__(self):
        return f'{self.store} : {self.accountname} - {self.accountcode} > {self.accounttypelist}'    


class AccountTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE,related_name="accountstransaction")
    transactiondate = models.DateTimeField()
    transactiontype = models.CharField(max_length=20)
    transactionamount = models.FloatField()
    transactionrealted= models.CharField(max_length=255,null=True,blank=True)
    transactiondetails = models.TextField(null=True,blank=True)
    transactionid = models.CharField(max_length=255,null=True,blank=True)
    previousprtransactiontype = models.CharField(max_length=20,null=True)
    previousamount = models.FloatField()
    remainingamount = models.FloatField()
    isverified = models.BooleanField(default=False)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return 'Wallet Transaction ID '+str(self.id)


class ManualJournalVoucher(models.Model):
    store = models.ForeignKey("store_app.Store", on_delete = models.CASCADE, null = True, blank = True)
    admin = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True,related_name="juurnaladmins")
    referenceno = models.CharField(max_length = 255, null = True, blank = True)
    createddate= models.DateField(null = True, blank = True)
    transactiontype=models.CharField(max_length = 255, null = True, blank = True)
    description=models.TextField( null = True, blank = True)
    totaldebit  = models.FloatField( default = 0.00, null =True, blank = True)
    totalcredit = models.FloatField( default = 0.00, null = True, blank = True)
    amount = models.FloatField( default = 0.00, null = True, blank = True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

def __str__(self):
        return str(self.id) + ' ' +str(self.store)


class AccountEntry(models.Model):
    manualjournalvoucher= models.ForeignKey(ManualJournalVoucher, on_delete=models.CASCADE, null=True, blank=True,related_name="manualjournalvouchers")
    account= models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    transactiontype=models.CharField(max_length = 255, null = True, blank = True)
    totaldebit  = models.FloatField( default = 0.00, null =True, blank = True)
    totalcredit = models.FloatField( default = 0.00, null = True, blank = True)
    amount = models.FloatField( default = 0.00, null = True, blank = True)
    balance         =  models.FloatField( default = 0.00, null = True, blank = True)
    ismatched      = models.BooleanField(default=False,null = True, blank = True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    
    def __str__(self):
        return str(self.id)













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







