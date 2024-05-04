from django.db import models
from store_app.models import *
from django.core.exceptions import ValidationError
# Create your models here.
from django.utils.safestring import mark_safe
from ckeditor.fields import RichTextField
from admin_app.models import *
## Image
import imghdr
from io import BytesIO
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def compressImage(product_img):
    IMAGE_x = imghdr.what(product_img)
    print(IMAGE_x,'IMAGE_x')
    im = Image.open(product_img)
    output = BytesIO()
    # Resize/modify the image
    im = im.resize((500, 500))
    # after modifications, save it to the output
    im.save(output, format=f'{IMAGE_x}', quality=90)
    output.seek(0)
    # change the imagefield value to be the newley modifed image value
    product_img = InMemoryUploadedFile(output, 'ImageField', F"%s.{IMAGE_x}" % product_img.name.split('.')[0], F'image/{IMAGE_x}',sys.getsizeof(output), None)
    return product_img




class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='inventory/category', null=True,blank=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.name

class ProductSubCategory(models.Model):
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	image = models.FileField(upload_to='inventory/subcategory', null=True,blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return self.name

class ProductSubSubCategory(models.Model):
	subcategory = models.ForeignKey(to=ProductSubCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	image = models.FileField(upload_to='inventory/subsubcategory', null=True,blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return self.name


class Brand(models.Model):
	name = models.CharField(max_length=255)
	image = models.FileField(upload_to='inventory/brand', null=True,blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	
	def __str__(self):
		return str(self.name)
	
### Color ---- Only
class FirstVariant(models.Model):   
	COLOR= (
        ('Color', 'Color'),
    )
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=255,choices=COLOR)
	store = models.ManyToManyField(Store, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.name)
	
class FirstVariantValue(models.Model):
	firstvariant = models.ForeignKey(to=FirstVariant, on_delete=models.CASCADE)
	value = models.CharField(max_length=255)
	store = models.ManyToManyField(Store, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.value)
	
#### Storage 

Sencondchocice=[
        ('Storage','Storage'),
        ('Size','Size'),
        ('Capacity','Capacity'),
        ('Display Size','Display Size'),
        ('Weight','Weight'),
        ('Thal','Thal'),
        ('Unit','Unit'),
        ('Dimension','Dimension'),
        ('Power Consumption','Power Consumption')
        
]
class SecondVariant(models.Model):
	
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=255,choices=Sencondchocice)
	store = models.ManyToManyField(Store, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.name)
	
class SecondVariantValue(models.Model):
	secondvariant = models.ForeignKey(to=SecondVariant, on_delete=models.CASCADE)
	value = models.CharField(max_length=255)
	store = models.ManyToManyField(Store, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.value)
	

# Custom validator 
RESTRICTED_VALUES = ['Storage', 'Color', 'Size','Capacity','Display Size','Weight','Thal','Unit','Dimension','Power Consumption']
def validate_other(value):
    if value in RESTRICTED_VALUES:
        raise ValidationError(f'{value} not allowed.')    
	
### Other	
class ThirdVariant(models.Model):
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=255,validators=[validate_other])
	store = models.ManyToManyField(Store, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.name)
	
class ThirdVariantValue(models.Model):
	thirdvariant = models.ForeignKey(to=ThirdVariant, on_delete=models.CASCADE)
	value = models.CharField(max_length=255)
	store = models.ManyToManyField(Store, blank=True)
	isactive = models.BooleanField(default=True)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	
	def __str__(self):
		return str(self.value)

class Unit(models.Model):
    name = models.CharField(max_length=250,null=True, blank=True)
    symbol = models.CharField(max_length=250,null=True, blank=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)



class Product(models.Model):
    store = models.ForeignKey(Store,on_delete=models.CASCADE,null=True, blank=True)
    category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE,null=True, blank=True)
    subcategory = models.ForeignKey(ProductSubCategory,on_delete=models.CASCADE,null=True, blank=True)
    subsubcategory = models.ForeignKey(ProductSubSubCategory,on_delete=models.CASCADE,null=True, blank=True)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE, null=True, blank=True)
    productname = models.CharField(max_length=250,null=True, blank=True)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,null=True, blank=True)
    description =RichTextField(null=True, blank=True)
    hsn= models.IntegerField(blank=True, null=True)
    tax= models.FloatField(default=0.00,null=True)
    pv = models.FloatField(default=0.00,null=True)
    admincommission = models.FloatField(default=0.00,null=True)
    frequentlyboughttogetherproduct=models.ManyToManyField('Product',blank=True,related_name="FrequentlyBoughtTogether")
    isproductrejected=models.BooleanField(default=False,null=True,blank=True)
    reasonforproductrejected=models.TextField(null=True,blank=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.productname


class ProductVariants(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
    store = models.ForeignKey(Store,on_delete=models.CASCADE,null=True, blank=True)
    sku=models.CharField(max_length=255,null=True,blank=True,unique=True)
    upc=models.CharField(max_length=255,null=True,blank=True,unique=True)
    barcodeimage=models.ImageField(upload_to='inventory/productvariant/barcodeimage',null=True, blank=True)
    firstvariantvalue = models.ForeignKey(FirstVariantValue,on_delete=models.CASCADE, null=True, blank=True)
    secondvariantvalue = models.ForeignKey(SecondVariantValue,on_delete=models.CASCADE, null=True, blank=True)
    thirdvariantvalue = models.ForeignKey(ThirdVariantValue,on_delete=models.CASCADE, null=True, blank=True)
    productvariantname=models.CharField(max_length=255,null=True,blank=True)
    productimage=models.ImageField(upload_to='inventory/productvariant/productimage',null=True, blank=True)
    quantity=models.PositiveIntegerField(default=1)
    mrp=models.FloatField(default=0.00)
    purchaseprice=models.FloatField(default=0.00,null=True,blank=True)
    price=models.FloatField(default=0.00)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.productvariantname
    def save(self, *args, **kwargs):
        if not self.id:
            self.productimage = compressImage(self.productimage)
        super(ProductVariants, self).save(*args, **kwargs)



class ProductImages(models.Model):
    productvariants = models.ForeignKey(ProductVariants,on_delete=models.CASCADE,blank=True,null=True)
    image = models.FileField(upload_to='inventory/productvariant/productvariantimages',blank=True,null=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.productvariants.productvariantname + 'Images' + str(self.image)

    def save(self, *args, **kwargs):
        if not self.id:
            self.image = compressImage(self.image)
        super(ProductImages, self).save(*args, **kwargs)

            


     
class ProductVariantSpecification(models.Model):
    category=models.ForeignKey(ProductCategory,on_delete=models.SET_NULL,null=True,blank=True)
    specificationname=models.CharField(max_length=255,null=True)
    store = models.ManyToManyField(Store,blank=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self):
        return str(self.name)

class ProductVariantSpecificationType(models.Model):
    productvariantspecification=models.ForeignKey(ProductVariantSpecification,on_delete=models.CASCADE,null=True,blank=True)
    specificationtype=models.CharField(max_length=255,null=True)
    store = models.ManyToManyField(Store,blank=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self):
        return str(self.specificationtype) + " " + str(self.productvariantspecification.specificationname)

class ProductVariantsSpecificatonValue(models.Model):
    productvariants = models.ForeignKey(ProductVariants, on_delete=models.CASCADE,blank=True,null=True)
    specificationtype=models.ForeignKey(ProductVariantSpecificationType,on_delete=models.CASCADE,null=True,blank=True)
    specificationvalue=models.TextField(null=True,blank=True)
    isactive = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedon = models.DateTimeField(auto_now=True)
    updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return str(self.specificationtype) +" "+ str(self.productvariants)

