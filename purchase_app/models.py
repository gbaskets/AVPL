# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from accountant_app.models import Account
from customer_app.models import *
from inventory_app.models import *
from store_app.models import Store
from vendor_app.models import *
from main_app.models import *
# Create your models here.
import random
import string

def generate_order_number(id):
    prefix = f'ORD{id}'  # Prefix for the order number
    length = 8  # Length of the random part of the order number

    # Generate a random string of digits and uppercase letters
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    return f"{prefix}{random_part}"

class PurchasesOrder(models.Model):
    type=models.CharField(max_length=250, null=True, blank=True)
    store = models.ForeignKey(Store,on_delete=models.CASCADE,null=True, blank=True)
    orderno=models.CharField(max_length=250, null=True, blank=True)
    supplierinvoiceno=models.CharField(max_length=250, null=True, blank=True)
    selleraccount = models.ForeignKey(Account, on_delete=models.CASCADE,  null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,  null=True, blank=True)
    vendor = models.ForeignKey('vendor_app.Vendor', on_delete=models.CASCADE, null=True, blank=True)
    paymenttransaction = models.ForeignKey("main_app.PaymentTransaction",on_delete=models.CASCADE, null=True, blank=True)
    address = models.ForeignKey(Address,on_delete=models.CASCADE,null=True,blank=True)
    shippingcharges = models.FloatField(default=0.00,null=True,blank=True)
    subtotal = models.FloatField(default=0.00,null=True,blank=True)
    tax = models.FloatField(default=0.00,null=True,blank=True)
    total = models.FloatField(default=0.00,null=True,blank=True)
    totaladmincommission = models.FloatField(default=0.00,null=True,blank=True)
    description=models.CharField(max_length=250, null=True, blank=True)
    pv = models.FloatField(default=0.00)
    selfpickup = models.BooleanField(default=False)
    ispaymentpaid = models.BooleanField(default=False)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    
    def save(self, *args, **kwargs):
        if not self.orderno:
            # Generate your order number here
            self.orderno = generate_order_number(self.id)  # You need to implement this function
        super().save(*args, **kwargs)
        
    def taxtype(self):
        if self.store.state == self.address.state :
            taxtype='GST'
        else:
            taxtype='IGST'
        return taxtype
    
    
    def taxgst(self):    
        perproducttax= round((self.tax /2),2)
        return perproducttax
      
  
    def __str__(self):
        return 'Order ID  '+str(self.id) + '  ' +str(self.customer)

class PurchasesOrderItems(models.Model):
    STATUS_CHOICES = (
    ("None", "None"),
    ("Pending", "Pending"),
    ("Accepted", "Accepted"),
    ("Rejected", "Rejected")
    )
    store = models.ForeignKey(Store,on_delete=models.CASCADE)
    purchasesorder = models.ForeignKey(PurchasesOrder,on_delete=models.CASCADE,related_name="purchasesorders")
    productvariants = models.ForeignKey(ProductVariants, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField()
    price = models.FloatField(default=0.00,null=True,blank=True)
    tax = models.FloatField(default=0.00,null=True,blank=True)
    admincommission = models.FloatField(default=0.00,null=True,blank=True)
    total =  models.FloatField(default=0.00,null=True,blank=True)
    orderstatus = models.CharField(max_length=255, default='Pending',null=True,blank=True)
    deliveryexpected = models.DateField(null=True, blank=True)
    deliveredon=models.DateTimeField(null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    cancellationreason = models.CharField(max_length=500, null=True, blank=True)
    cancelledon = models.DateTimeField(null=True, blank=True)
    
    def taxtype(self):
        if self.store.state == self.purchasesorder.address.state :
            taxtype='GST'
        else:
            taxtype='IGST'
        return taxtype
        
    
    def taxgst(self):    
        perproducttax= round((self.tax /2),2)
        return perproducttax
    
  
    def __str__(self):
        return self.productvariants.productvariantname + 'purchasesorder' + str(self.purchasesorder.id) + 'purchasesorderitem' + str(self.id)
