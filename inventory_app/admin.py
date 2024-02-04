from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(ProductCategory)
admin.site.register(ProductSubCategory)
admin.site.register(ProductSubSubCategory)
admin.site.register(FirstVariant)
admin.site.register(FirstVariantValue)
admin.site.register(SecondVariant)
admin.site.register(SecondVariantValue)
admin.site.register(ThirdVariant)
admin.site.register(ThirdVariantValue)
admin.site.register(Product)
admin.site.register(ProductVariants)
admin.site.register(ProductImages)
admin.site.register(ProductVariantSpecification)
admin.site.register(ProductVariantSpecificationType)
admin.site.register(ProductVariantsSpecificatonValue)