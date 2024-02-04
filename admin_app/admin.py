from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from django.utils.html import format_html




class BannerAdmin(admin.ModelAdmin):
	list_display = ['title', 'subtitle', 'description', 'link', 'image']

class VariantAdmin(admin.ModelAdmin):
	list_display = ['name']



class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'tax', 'image']
	def image_tag(self,obj):
		image_str = '<img src="{0}" style="width: 45px; height:45px;" />'.format(obj.image.url)

class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ['category', 'name', 'image']
	def image_tag(self,obj):
		image_str = '<img src="{0}" style="width: 45px; height:45px;" />'.format(obj.image.url)

class SubSubCategoryAdmin(admin.ModelAdmin):
	list_display = ['subcategory', 'name', 'image']
	def image_tag(self,obj):
		image_str = '<img src="{0}" style="width: 45px; height:45px;" />'.format(obj.image.url)

class PointValueAdmin(admin.ModelAdmin):
	list_display = ['category', 'percentage']

class BrandAdmin(admin.ModelAdmin):
	list_display = ['category', 'name']


admin.site.register(HomeBanner, BannerAdmin)

admin.site.register(AboutUs)
admin.site.register(Blog)
admin.site.register(Gallery)

admin.site.register(HomeFooterBanner)
