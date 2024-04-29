import os
from django.shortcuts import render
from django.conf import settings
# Create your views here.
import re
import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.http import HttpResponse
from requests import request
from inventory_app.models import *
from sales_app.models import SalesOrderItems
from vendor_app.models import *
from main_app.models import *
from admin_app.models import *
from django.http import JsonResponse
from vendor_app.utils import *
from main_app.utils import *
from django.utils import timezone

ORDER_STATUS_UPDATE = (
    ("Order Placed", "Order Placed"),
    ("Packed", "Packed"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    
)

def vendor_home(request):
	return render(request, 'vendor_app/dashboard.html')



@csrf_exempt
def vendor_dashboard(request):
	if check_user_authentication(request, 'VENDOR'):
		if Vendor.objects.filter(user=request.user).exists():
			...
			
			vendor = Vendor.objects.get(user=request.user)
			if vendor.verified and vendor.storecreated :
                
				storeobj=Store.objects.filter(vendor=vendor).first()
       

				if not Wallet.objects.filter(vendor=vendor).exists():
					Wallet.objects.create(vendor=vendor)
				wallet = Wallet.objects.get(vendor=vendor)
				transactions = WalletTransaction.objects.filter(wallet=wallet)

				if not BusinessLimitWallet.objects.filter(vendor=vendor).exists():
					BusinessLimitWallet.objects.create(vendor=vendor,isactive=True)
				business_limit = BusinessLimitWallet.objects.filter(vendor=vendor,isactive=True).first()
				business_limit_transactions = BusinessLimitWalletTransaction.objects.filter(businesslimitwallet=business_limit)

				if not CommissionWallet.objects.filter(vendor=vendor).exists():
					CommissionWallet.objects.create(vendor=vendor,isactive=True)
				wallet_commission = CommissionWallet.objects.filter(vendor=vendor,isactive=True).first()
				
							
				dic = {'vendor':vendor, 'storeobj':storeobj,
				'allorder_status':ORDER_STATUS_UPDATE,'wallet':wallet,
                'business_limit':business_limit,
                'wallet_commission':wallet_commission,
				'business_limit_transactions':business_limit_transactions,
				'transactions':transactions,
				'notification_len':len(Notification.objects.filter(vendor=vendor, isread=False)),
				}
				return render(request, 'vendor_app/dashboard.html', dic)

			elif vendor.verified == False:
				return redirect('/vendor/verification')

			elif vendor.storecreated == False:
				return redirect('/vendor/storeinfo')

			else:
				return render(request, 'vendor_app/store_message.html')

     
		else:
			return redirect('/vendor/verification')
	else:
		return redirect('/login/')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def order_status_update(request):

	vendor = Vendor.objects.filter(user=request.user)
		
	if request.method == "POST":
		order_id = request.POST.get('order_id')
		order = Orders.objects.filter(id=order_id).first()
		delivery_status=request.POST.get('delivery_status')
		
		order.delivery_status = delivery_status
		order.save()
		
		messages.success(
			request, f"The order status of order_id ORD{order_id} has been updated ! ")
		vendor = Vendor.objects.filter(user=request.user)
		if delivery_status == 'Delivered':
			OrderItems.objects.filter(order=order_id).update(delivery_status=delivery_status, delivered_on=timezone.now())
			users = OrderItems.objects.filter(order=order_id).first()
			user=users.order.user
			print(user)
			order=users.order
			print(order)
			
				
			order_item = OrderItems.objects.filter(order=order_id)
			print(order_item)
			for x in order_item:
				print(x.plan,'LLLLLLLLLLLLLLLLLLLLLLLLLLLL')
				save_pv_transaction(user, x.product, x.subtotal, x.plan)
			if not order.paid:
				orderitems = OrderItems.objects.filter(order=order_id).first()
				print(orderitems,'OOOOOOOOO')
				admin_commission = (orderitems.total/100)*orderitems.product.category.commission
				print("admin commission percentage")
				print(orderitems.product.category.commission)
				print(admin_commission,'KKKKKKKKKKKKKK')
				gst = (admin_commission/100)*18   #GST of 18 per on admin charge deduct from businesslimit
				print(gst)
				admin_commission_plus_gst = admin_commission + gst
				print("printing total_detection_amt")
				print(admin_commission_plus_gst)
				GST_Log.objects.create(orders = orderitems, gst_amt=gst)
				trans_name = 'Transaction for ORD'+str(order.id)+str(orderitems.id)
				#make_business_limit_transaction(vendor, admin_commission, 'DEBIT', trans_name)
				make_business_limit_transaction(vendor, admin_commission_plus_gst, 'DEBIT', trans_name)
				make_commission_transaction(vendor.user, admin_commission_plus_gst, 'CREDIT')
				user_c = 0.0
				if UserVendorRelation.objects.filter(vendor=vendor).exists():
					print('hhhhhhhhhhhhhhhh')
					user = UserVendorRelation.objects.get(vendor=vendor)
					percentage = float(str(UserVendorCommission.objects.get()))
					user_c = (orderitems.total/100) * percentage
					make_commission_transaction(user, admin_commission_plus_gst, 'CREDIT')
					make_wallet_transaction(vendor.user, user_c, 'DEBIT')
		else:
			OrderItems.objects.filter(order=order_id).update(delivery_status=delivery_status)
			notification(vendor.user, 'Order '+delivery_status)

			# orderitem= OrderItems.objects.filter(order=order_id)
			# print(orderitem,'oitem')
			# for item in orderitem:  
			# 	item.delivery_status = delivery_status 
			# 	item.save()
		
	return redirect('/vendor')
@csrf_exempt
def order_status_updates(request):

	vendor = Vendor.objects.filter(user=request.user)
	if request.method == "POST":
		order_id = request.POST.get('order_id')
		order = Orders.objects.filter(id=order_id).first()
		delivery_status=request.POST.get('delivery_status')
		
		order.delivery_status = delivery_status
		order.save()
		
		messages.success(
			request, f"The order status of order_id ORD{order_id} has been updated ! ")
		vendor = Vendor.objects.filter(user=request.user)
		if delivery_status == 'Delivered':
			OrderItems.objects.filter(order=order_id).update(delivery_status=delivery_status, delivered_on=timezone.now())
			users = OrderItems.objects.filter(order=order_id).first()
			user=users.order.user
			print(user)
			order=users.order
			print(order)
			order_item = OrderItems.objects.filter(order=order_id)
			print(order_item)
			for x in order_item:
				print(x.plan,'LLLLLLLLLLLLLLLLLLLLLLLLLLLL')
				save_pv_transaction(user, x.product, x.subtotal, x.plan)
			if not order.paid:
				orderitems = OrderItems.objects.filter(order=order_id).first()
				admin_commission = (orderitems.total/100)*orderitems.product.category.commission
				print("admin commission percentage")
				print(orderitems.product.category.commission)
				print(admin_commission,'KKKKKKKKKKKKKK')
				gst = (admin_commission/100)*18   #GST of 18 per on admin charge deduct from businesslimit
				print(gst)
				admin_commission_plus_gst = admin_commission + gst
				print("printing total_detection_amt")
				print(admin_commission_plus_gst)
				GST_Log.objects.create(orders = orderitems, gst_amt=gst)
				trans_name = 'Transaction for ORD'+str(order.id)+str(orderitems.id)
				#make_business_limit_transaction(vendor, admin_commission, 'DEBIT', trans_name)
				print(trans_name,'TTTTTTT')
				make_business_limit_transaction(vendor, admin_commission_plus_gst, 'DEBIT', trans_name)
				make_commission_transaction(vendor.user, admin_commission_plus_gst, 'CREDIT')
				user_c = 0.0
				if UserVendorRelation.objects.filter(vendor=vendor).exists():
					print('hhhhhhhhhhhhhhhh')
					user = UserVendorRelation.objects.get(vendor=vendor)
					percentage = float(str(UserVendorCommission.objects.get()))
					user_c = (orderitems.total/100) * percentage
					make_commission_transaction(user, admin_commission_plus_gst, 'CREDIT')
					make_wallet_transaction(vendor.user, user_c, 'DEBIT')
		else:
			OrderItems.objects.filter(order=order_id).update(delivery_status=delivery_status)
			notification(vendor.user, 'Order '+delivery_status)

			# orderitem= OrderItems.objects.filter(order=order_id)
			# print(orderitem,'oitem')
			# for item in orderitem:  
			# 	item.delivery_status = delivery_status 
			# 	item.save()
		
	return redirect('/vendor/orders')

@csrf_exempt
def store_info(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.get(user=request.user)	
		if request.method == 'POST':
			vendor = Vendor.objects.get(user=request.user)
			storename = request.POST.get('storename')
			description = request.POST.get('description')
			streetaddress =  request.POST.get('streetaddress')
			nearbyaddress =  request.POST.get('nearbyaddress')
			pincode = request.POST.get('pincode')
			city= request.POST.get('city')
			state= request.POST.get('state')
			country= request.POST.get('country')
			latitude =  request.POST.get('latitude')
			longitude =  request.POST.get('longitude')
			
			
			logo = request.FILES.get('logo')
			banner = request.FILES.get('banner')
			closing_day = request.POST.get('closing_day')
			closing_time = request.POST.get('closing_time')
			opening_time = request.POST.get('opening_time')
   
            #Doc
			storeregistrationtype=request.POST.get('storeregistrationtype')
			msmeno=request.POST.get('msmeno')
			msmedoc = request.FILES.get('msmedoc')
			pancardno=request.POST.get('pancardno')
			pancarddoc = request.FILES.get('pancarddoc')
			gstno=request.POST.get('gstno')
			gstnodoc = request.FILES.get('gstnodoc')

			#policy
			shippingpolicy =request.POST.get('shippingpolicy')
			replacementpolicy = request.POST.get('replacementpolicy')
			returnandrefundpolicy = request.POST.get('returnandrefundpolicy')
			businessmaincategory =request.POST.get('businessmaincategory')
			businesscategory =request.POST.getlist('businesscategory')

			
			if not Store.objects.filter(vendor = vendor,storename=storename).exists():
				storeobj=Store.objects.create(vendor = vendor,storename=storename)
                # Generate a random registration number
				registration_number = f'{storeobj.vendor.mobile}{storeobj.storename.replace(" ", "")}'

				# Generate QR code
				qr = qrcode.QRCode(
					version=1,
					error_correction=qrcode.constants.ERROR_CORRECT_L,
					box_size=10,
					border=4,
				)
				qr.add_data(str(registration_number))
				qr.make(fit=True)
				qr_image = qr.make_image(fill_color="black", back_color="white")

				# Define the directory to save the QR code image
				qr_image_directory = os.path.join('store', 'qrcode')  # Relative to MEDIA_ROOT
				os.makedirs(os.path.join(settings.MEDIA_ROOT, qr_image_directory), exist_ok=True)  # Ensure directory exists

				# Save QR code image
				qr_image_path = os.path.join(qr_image_directory, f"{registration_number}.png")
				qr_image_full_path = os.path.join(settings.MEDIA_ROOT, qr_image_path)
				qr_image.save(qr_image_full_path)


				# Update storeobj with registration number and QR code path
				storeobj.registrationno = registration_number 
				storeobj.registrationqrcode = qr_image_path
				storeobj.save()
			else:
				storeobj=Store.objects.filter(vendor = vendor,storename=storename).first()
			    
				# Generate a random registration number
				registration_number = f'{storeobj.vendor.mobile}{storeobj.storename.replace(" ", "")}'

				# Generate QR code
				qr = qrcode.QRCode(
					version=1,
					error_correction=qrcode.constants.ERROR_CORRECT_L,
					box_size=10,
					border=4,
				)
				qr.add_data(str(registration_number))
				qr.make(fit=True)
				qr_image = qr.make_image(fill_color="black", back_color="white")

				# Define the directory to save the QR code image
				qr_image_directory = os.path.join('store', 'qrcode')  # Relative to MEDIA_ROOT
				os.makedirs(os.path.join(settings.MEDIA_ROOT, qr_image_directory), exist_ok=True)  # Ensure directory exists

				# Save QR code image
				qr_image_path = os.path.join(qr_image_directory, f"{registration_number}.png")
				qr_image_full_path = os.path.join(settings.MEDIA_ROOT, qr_image_path)
				qr_image.save(qr_image_full_path)


				# Update storeobj with registration number and QR code path
				storeobj.registrationno = registration_number 
				storeobj.registrationqrcode = qr_image_path
				storeobj.save()
				
			if businessmaincategory:
				businessmaincategory_obj=BusinessMainCategory.objects.filter(id=businessmaincategory).first()
				storeobj.businessmaincategory=businessmaincategory_obj
			
			if businesscategory:
		
				for category_id in businesscategory:
					businesscategory_obj=BusinessCategory.objects.filter(id=category_id).first()
					storeobj.businesscategory.add(businesscategory_obj)
					storeobj.save()
			if storeregistrationtype:
				storeobj.storeregistrationtype=storeregistrationtype	
		
			if description:
				storeobj.description = description
    
			if streetaddress:
				storeobj.streetaddress = streetaddress
			if nearbyaddress:	
				storeobj.nearbyaddress =nearbyaddress
			if pincode:
				storeobj.pincode = pincode
			if city:
				storeobj.city=city
			if state:
				storeobj.state=state
			if country:
				storeobj.country=country
			if latitude:
				storeobj.latitude = latitude
			if longitude:
				storeobj.longitude = longitude
			if logo:
				storeobj.logo = logo
			if banner:
				storeobj.banner = banner

			#Doc
			if msmeno:
				storeobj.msmeno=msmeno
			if msmedoc:
				storeobj.msmedoc = msmedoc
			if pancardno:
				storeobj.pancardno=pancardno
			if pancarddoc:
				storeobj.pancarddoc = pancarddoc
			if gstno:
				storeobj.gstno=gstno
			if gstnodoc:
				storeobj.gstnodoc = gstnodoc

				#policy
			if shippingpolicy:
				storeobj.shippingpolicy =shippingpolicy
			if replacementpolicy:
				storeobj.replacementpolicy = replacementpolicy
			if returnandrefundpolicy:
				storeobj.returnandrefundpolicy = returnandrefundpolicy
    
			if returnandrefundpolicy:
				storeobj.closingday = closing_day
			if returnandrefundpolicy:
				storeobj.closingtime = closing_time
			if returnandrefundpolicy:
				storeobj.openingtime = opening_time
			storeobj.save()

			
			Vendor.objects.filter(id=vendor.id).update(storecreated=True,docsubmitted=True)
			messages.info(request, 'Store Created Successfully !!!!')
			return redirect('/vendor/')
		businessmaincategory_obj=BusinessMainCategory.objects.filter(isactive=True)
		businesscategory_obj=BusinessCategory.objects.filter(isactive=True)
        
		if Store.objects.filter(vendor=vendor).exists():
			storeobj = Store.objects.get(vendor=vendor)
		else:
			storeobj=""
		dic={"businessmaincategory_obj":businessmaincategory_obj,
				"businesscategory_obj":businesscategory_obj,
                 "storeobj":storeobj,
				}
		return render(request, 'vendor_app/store-register.html',dic )
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_doc(request):
	if check_user_authentication(request, 'VENDOR'):
     
		if request.method == 'POST':
    	
			mobile = request.POST.get('mobile')
			email = request.POST.get('email')
			firstname= request.POST.get('firstname')
			lastname= request.POST.get('lastname')
			gender =  request.POST.get('gender')
			dob= request.POST.get('dob')
			streetaddress =  request.POST.get('streetaddress')
			nearbyaddress =  request.POST.get('nearbyaddress')
			pincode = request.POST.get('pincode')
			city= request.POST.get('city')
			state= request.POST.get('state')
			country= request.POST.get('country')
			latitude =  request.POST.get('latitude')
			longitude =  request.POST.get('longitude')
			profilepic = request.FILES.get('profilepic')

			#Personal User 
   
			pancardno=request.POST.get('pancardno')
			pancarddoc = request.FILES.get('pancarddoc')
			idproof= request.POST.get('idproof')
			idno= request.POST.get('idno')
			frontidproofdoc = request.FILES.get('frontidproofdoc')
			backidproofdoc=request.FILES.get('backidproofdoc')
			addressproof= request.POST.get('addressproof')
			addressno= request.POST.get('addressno')
			frontaddressproofdoc =request.FILES.get('frontaddressproofdoc')
			backddressproofdoc = request.FILES.get('backddressproofdoc')
			
			print(mobile,'Mobile')
    
			if not Vendor.objects.filter(user=request.user).exists():
				vendor_obj=Vendor.objects.create(user=request.user)
			else:
				vendor_obj=Vendor.objects.filter(user=request.user).first()
				
				user=User.objects.filter(id=request.user.id).first()
		
				if mobile:
					vendor_obj.mobile = mobile
					user.username=mobile
				if email:
					user.email=email
				if firstname:
					vendor_obj.firstname= firstname
					user.first_name=firstname
				if lastname:
					vendor_obj.lastname= lastname
					user.last_name=lastname
				if gender:
					vendor_obj.gender =  gender
				if dob:
					vendor_obj.dob= dob
				if streetaddress:
					vendor_obj.streetaddress =  streetaddress
				if nearbyaddress:
					vendor_obj.nearbyaddress =  nearbyaddress
				if pincode:
					vendor_obj.pincode = pincode
				if city:
					vendor_obj.city= city
				if state:
					vendor_obj.state= state
				if country:
					vendor_obj.country= country
				if latitude:
					vendor_obj.latitude =  latitude
				if longitude:
					vendor_obj.longitude =  longitude
				if profilepic:
					vendor_obj.profilepic =profilepic

				#Personal User 
				if profilepic:
					vendor_obj.pancardno=pancardno
				if profilepic:
					vendor_obj.pancarddoc =pancarddoc
				if profilepic:
					vendor_obj.idproof= idproof
				if profilepic:
					vendor_obj.idno= idno
				if profilepic:
					vendor_obj.frontidproofdoc =frontidproofdoc
				if profilepic:
					vendor_obj.backidproofdoc=backidproofdoc
				if profilepic:
					vendor_obj.addressproof= addressproof
				if profilepic:
					vendor_obj.addressno= addressno
				if profilepic:
					vendor_obj.frontaddressproofdoc =frontaddressproofdoc
				if profilepic:
					vendor_obj.backddressproofdoc =backddressproofdoc
				user.save()

				vendor_obj.save()
				messages.info(request, 'Your data has been saved !')

# 			sub = 'AVPL - Thank You For Submitting KYC Documents'
# 			msg = '''Hi there!
# We got your documents for KYC, we will verify them soon and let you know,

# Thanks!'''  
# 			if request.user.email :
# 				EmailMessage(sub,msg,to=[request.user.email]).send()

			return redirect('/vendor/storeinfo')
		else:
			if Vendor.objects.filter(user=request.user).exists():
				vendor_obj=Vendor.objects.filter(user=request.user).first()
				if vendor_obj.storecreated ==True and vendor_obj.docsubmitted == True :
					flag=vendor_obj.docsubmitted
				else:
					flag=""
                    
			     
				# dic = {'vendor':vendor, 'flag':vendor.doc_submitted}
				dic={'vendor':vendor_obj, 'flag':flag}
			else:
				dic={'vendor':{}}

			return render(request, 'vendor_app/vendor-doc.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




def get_businesscategory(request):
	category_id = request.GET.get('category_id')
	businesscategory_obj=BusinessCategory.objects.filter(isactive=True,businessmaincategory__id=category_id)
	subcategory_list = list(businesscategory_obj.values())
	print(subcategory_list,'subcategory_list')
	return JsonResponse({'data':subcategory_list})




@csrf_exempt
def vendor_product_list(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		dic = {
			'vendor':vendor,
			'categories':ProductCategory.objects.all(),
			'subcategories':ProductSubCategory.objects.all(),
			'subsubcategories':ProductSubSubCategory.objects.all(),
			'brands':Brand.objects.all(),
			'products':Product.objects.filter(store__vendor__user=request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product/product-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def add_product(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':

			vendor = Vendor.objects.filter(user=request.user).first()
			store = Store.objects.filter(vendor=vendor).first()
			category_id=request.POST.get('category_id') 
			subcategory_id=request.POST.get('subcategory_id') 
			subsubcategory_id=request.POST.get('subsubcategory_id') 
			brand_id=request.POST.get('brand_id') 
			productname=request.POST.get('productname') 
			description=request.POST.get('description') 
			hsn=request.POST.get('hsn') 
			tax=request.POST.get('tax') 
			pv=request.POST.get('pv') 
			admincommission=request.POST.get('admincommission') 
	
			if Product.objects.filter(store=store, productname=productname).exists():
				messages.info(request, f'Product: {productname} is already exits !')
				return redirect('/vendor/product-list')
			else:
				if productname and category_id :				
					pro = Product.objects.create(store = store,productname = productname,description = description)
					if category_id:
						pro.category = ProductCategory.objects.get(id=category_id)
					if subcategory_id:
						pro.subcategory = ProductSubCategory.objects.get(id=subcategory_id)
					if subsubcategory_id:
						pro.subsubcategory = ProductSubSubCategory.objects.get(id=subsubcategory_id)
					if brand_id:
						pro.brand = Brand.objects.get(id=brand_id)
					if hsn:
						pro.hsn= hsn
					if hsn:
						pro.tax= tax
					if hsn:
						pro.pv =pv
					if hsn:
						pro.admincommission =admincommission

					pro.updatedby= request.user
					pro.save()
					messages.success(request,f'Product {productname} is Added Successfully')
				else:
					messages.info(request, f'Please fill all detials such as productname and category !')
					return redirect('/vendor/product-list')
		dic = {
			'categories':ProductCategory.objects.all(),
			'subcategories':ProductSubCategory.objects.all(),
			'subsubcategories':ProductSubSubCategory.objects.all(),
			'brands':Brand.objects.all(),
			'products':Product.objects.filter(store__vendor__user=request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product/product-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

		
		
@csrf_exempt
def add_product_images(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			vendor = Vendor.objects.filter(user=request.user)
			images = request.FILES.getlist('images')
			product = Product.objects.get(id=request.session['product'])
			for image in images:
				ProductImages.objects.create(product=product,image=image)
			messages.success(request, 'Product Images Added Successfully')
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'variants':Variant.objects.all(),
				'variant':True,
				'product':product,
				# 'notification':get_notifications(request.user),
				# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request,'vendor_app/add-product.html', dic)
		else:
			vendor = Vendor.objects.filter(user=request.user)
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'info':True,
				# 'notification':get_notifications(request.user),
				# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request,'vendor_app/add-product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def add_product_variant(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			variant = Variant.objects.get(id=request.POST.get('variant'))
			variant_value = VariantValue.objects.get(id=request.POST.get('variantvalue'))
			variant_stock = request.POST.get('variantstock')
			product = Product.objects.get(id=request.session['product'])
			if ProductVariant.objects.filter(product=product, variant=variant, variant_value=variant_value).exists():
				return JsonResponse({'response':'failed'})
			ProductVariant.objects.create(product=product, variant=variant, variant_value=variant_value, variant_stock=variant_stock)
			data = ''
			for x in ProductVariant.objects.filter(product=product):
				data = data + '<tr><td>'+x.variant.name+'</td><td>'+x.variant_value.value+'</td><td>'+str(x.variant_stock)+'</td></tr>'
			return HttpResponse(data)
		else:
			vendor = Vendor.objects.filter(user=request.user)
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'info':True,
				# 'notification':get_notifications(request.user),
				# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			messages.success(request, 'Product has been added and added successfully. Now waiting for admin approval.')
			return render(request,'vendor_app/add-product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def fetch_sub_category(request):
	category = ProductCategory.objects.get(id=request.GET.get('cate'))
	subcategory = ProductSubCategory.objects.filter(category = category)
	data = '<option selected disabled>----select product sub category----</option>'
	for x in subcategory:
		data = data + '<option value="'+str(x.id)+'">'+x.name+'</option>'
	return HttpResponse(data)
@csrf_exempt
def fetch_variant_value(request):
	variant = Variant.objects.get(id=request.GET.get('variant'))
	data = ''
	for x in VariantValue.objects.filter(variant=variant):
		data = data + '<option value="'+str(x.id)+'">'+x.value+'</option>'
	return HttpResponse(data)
@csrf_exempt
def fetch_sub_sub_category(request):
	subcategory = ProductSubCategory.objects.get(id=request.GET.get('subcate'))
	subsubcategory = ProductSubSubCategory.objects.filter(subcategory = subcategory)
	data = '<option selected disabled>----select product sub sub category----</option>'
	for x in subsubcategory:
		data = data + '<option value="'+str(x.id)+'">'+x.name+'</option>'
	return HttpResponse(data)
@csrf_exempt
def fetch_brands(request):
	category = ProductCategory.objects.get(id = request.GET.get('cate'))
	brands = Brand.objects.filter(category=category)
	data = '<option selected disabled>----select product brand----</option>'
	for x in brands:
		data = data + '<option value="'+str(x.id)+'">'+x.name+'</option>'
	return HttpResponse(data)



@csrf_exempt
def vendor_profile(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		store = Store.objects.filter(vendor=vendor).first()
		businessmaincategory_obj=BusinessMainCategory.objects.filter(isactive=True)
		businesscategory_obj=BusinessCategory.objects.filter(isactive=True)
		
		
	
		dic = {
			'storeobj':store,
			'vendor':vendor,
            "businessmaincategory_obj":businessmaincategory_obj,
			"businesscategory_obj":businesscategory_obj,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}			
		return render(request,'vendor_app/vendor-profile.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def edit_vendor_profile(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			mobile = request.POST.get('mobile')
			email = request.POST.get('email')
			firstname= request.POST.get('firstname')
			lastname= request.POST.get('lastname')
			gender =  request.POST.get('gender')
			dob= request.POST.get('dob')
			streetaddress =  request.POST.get('streetaddress')
			nearbyaddress =  request.POST.get('nearbyaddress')
			pincode = request.POST.get('pincode')
			city= request.POST.get('city')
			state= request.POST.get('state')
			country= request.POST.get('country')
			latitude =  request.POST.get('latitude')
			longitude =  request.POST.get('longitude')
			profilepic = request.FILES.get('profilepic')

			#Personal User 
   
			pancardno=request.POST.get('pancardno')
			pancarddoc = request.FILES.get('pancarddoc')
			idproof= request.POST.get('idproof')
			idno= request.POST.get('idno')
			frontidproofdoc = request.FILES.get('frontidproofdoc')
			backidproofdoc=request.FILES.get('backidproofdoc')
			addressproof= request.POST.get('addressproof')
			addressno= request.POST.get('addressno')
			frontaddressproofdoc =request.FILES.get('frontaddressproofdoc')
			backddressproofdoc = request.FILES.get('backddressproofdoc')
   
			storename = request.POST.get('storename')
			description = request.POST.get('description')
			streetaddress =  request.POST.get('streetaddress')
			nearbyaddress =  request.POST.get('nearbyaddress')
			pincode = request.POST.get('pincode')
			city= request.POST.get('city')
			state= request.POST.get('state')
			country= request.POST.get('country')
			latitude =  request.POST.get('latitude')
			longitude =  request.POST.get('longitude')
			
			
			logo = request.FILES.get('logo')
			banner = request.FILES.get('banner')
			closing_day = request.POST.get('closing_day')
			closing_time = request.POST.get('closing_time')
			opening_time = request.POST.get('opening_time')

			#Doc
			storeregistrationtype=request.POST.get('storeregistrationtype')
			msmeno=request.POST.get('msmeno')
			msmedoc = request.FILES.get('msmedoc')
			pancardno=request.POST.get('pancardno')
			pancarddoc = request.FILES.get('pancarddoc')
			gstno=request.POST.get('gstno')
			gstnodoc = request.FILES.get('gstnodoc')

			#policy
			shippingpolicy =request.POST.get('shippingpolicy')
			replacementpolicy = request.POST.get('replacementpolicy')
			returnandrefundpolicy = request.POST.get('returnandrefundpolicy')
			businessmaincategory =request.POST.get('businessmaincategory')
			businesscategory =request.POST.getlist('businesscategory')

				
			
			print(mobile,'Mobile')
    
			
		
			vendor_obj=Vendor.objects.filter(user=request.user).first()
			
			user=User.objects.filter(id=request.user.id).first()
	
			if mobile:
				vendor_obj.mobile = mobile
				user.username=mobile
			if email:
				user.email=email
			if firstname:
				vendor_obj.firstname= firstname
				user.first_name=firstname
			if lastname:
				vendor_obj.lastname= lastname
				user.last_name=lastname
			if gender:
				vendor_obj.gender =  gender
			if dob:
				vendor_obj.dob= dob
			if streetaddress:
				vendor_obj.streetaddress =  streetaddress
			if nearbyaddress:
				vendor_obj.nearbyaddress =  nearbyaddress
			if pincode:
				vendor_obj.pincode = pincode
			if city:
				vendor_obj.city= city
			if state:
				vendor_obj.state= state
			if country:
				vendor_obj.country= country
			if latitude:
				vendor_obj.latitude =  latitude
			if longitude:
				vendor_obj.longitude =  longitude
			if profilepic:
				vendor_obj.profilepic =profilepic

			#Personal User 
			if profilepic:
				vendor_obj.pancardno=pancardno
			if profilepic:
				vendor_obj.pancarddoc =pancarddoc
			if profilepic:
				vendor_obj.idproof= idproof
			if profilepic:
				vendor_obj.idno= idno
			if profilepic:
				vendor_obj.frontidproofdoc =frontidproofdoc
			if profilepic:
				vendor_obj.backidproofdoc=backidproofdoc
			if profilepic:
				vendor_obj.addressproof= addressproof
			if profilepic:
				vendor_obj.addressno= addressno
			if profilepic:
				vendor_obj.frontaddressproofdoc =frontaddressproofdoc
			if profilepic:
				vendor_obj.backddressproofdoc =backddressproofdoc
			user.save()

			vendor_obj.save()


			
			
			storeobj=Store.objects.filter(vendor = vendor_obj).first()
			if storename:
				storeobj.storename=storename
				storeobj.save()

			# Generate a random registration number
			registration_number = f'{storeobj.vendor.mobile}{storeobj.storename.replace(" ", "")}'

			# Generate QR code
			qr = qrcode.QRCode(
				version=1,
				error_correction=qrcode.constants.ERROR_CORRECT_L,
				box_size=10,
				border=4,
			)
			qr.add_data(str(registration_number))
			qr.make(fit=True)
			qr_image = qr.make_image(fill_color="black", back_color="white")

			# Define the directory to save the QR code image
			qr_image_directory = os.path.join('store', 'qrcode')  # Relative to MEDIA_ROOT
			os.makedirs(os.path.join(settings.MEDIA_ROOT, qr_image_directory), exist_ok=True)  # Ensure directory exists

			# Save QR code image
			qr_image_path = os.path.join(qr_image_directory, f"{registration_number}.png")
			qr_image_full_path = os.path.join(settings.MEDIA_ROOT, qr_image_path)
			qr_image.save(qr_image_full_path)


			# Update storeobj with registration number and QR code path
			storeobj.registrationno = registration_number 
			storeobj.registrationqrcode = qr_image_path
			storeobj.save()
			
			if businessmaincategory:
				businessmaincategory_obj=BusinessMainCategory.objects.filter(id=businessmaincategory).first()
				storeobj.businessmaincategory=businessmaincategory_obj
			
			if businesscategory:
		
				for category_id in businesscategory:
					businesscategory_obj=BusinessCategory.objects.filter(id=category_id).first()
					storeobj.businesscategory.add(businesscategory_obj)
					storeobj.save()
			if storeregistrationtype:
				storeobj.storeregistrationtype=storeregistrationtype	
		
			if description:
				storeobj.description = description
	
			if streetaddress:
				storeobj.streetaddress = streetaddress
			if nearbyaddress:	
				storeobj.nearbyaddress =nearbyaddress
			if pincode:
				storeobj.pincode = pincode
			if city:
				storeobj.city=city
			if state:
				storeobj.state=state
			if country:
				storeobj.country=country
			if latitude:
				storeobj.latitude = latitude
			if longitude:
				storeobj.longitude = longitude
			if logo:
				storeobj.logo = logo
			if banner:
				storeobj.banner = banner

			#Doc
			if msmeno:
				storeobj.msmeno=msmeno
			if msmedoc:
				storeobj.msmedoc = msmedoc
			if pancardno:
				storeobj.pancardno=pancardno
			if pancarddoc:
				storeobj.pancarddoc = pancarddoc
			if gstno:
				storeobj.gstno=gstno
			if gstnodoc:
				storeobj.gstnodoc = gstnodoc

				#policy
			if shippingpolicy:
				storeobj.shippingpolicy =shippingpolicy
			if replacementpolicy:
				storeobj.replacementpolicy = replacementpolicy
			if returnandrefundpolicy:
				storeobj.returnandrefundpolicy = returnandrefundpolicy
	
			if returnandrefundpolicy:
				storeobj.closingday = closing_day
			if returnandrefundpolicy:
				storeobj.closingtime = closing_time
			if returnandrefundpolicy:
				storeobj.openingtime = opening_time
			storeobj.save()

			messages.info(request, 'Your Profile has been updated !')

		return redirect("/vendor/profile")
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_product(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		product = Product.objects.get(id=request.GET.get('id'))
		dic = {
			'vendor':vendor,
			'product':product,
			

			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request,'vendor_app/product/product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_update_product_quantity(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		product = Product.objects.get(id=id)

		if request.method == 'POST':
			vendor = Vendor.objects.filter(user=request.user)
			store = request.user.vendor.store
			stock = request.POST.get('stock')
			
			Product.objects.filter(id=id).update(
				stock = stock,
			
			)
			messages.success(request, 'Product quantity Updated Successfully')
			return redirect('/vendor/productlist')


		dic = {
			'vendor':vendor,
			'product':product,
			'images':ProductImages.objects.filter(product=product),
			'variants':ProductVariant.objects.filter(product=product),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request,'vendor_app/update-product-quantity.html', dic)

		
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_product_basic_edit(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			vendor = Vendor.objects.filter(user=request.user)
			store = request.user.vendor.store
			name = request.POST.get('name')
			des = request.POST.get('des')
			price = request.POST.get('price')
			mrp = request.POST.get('mrp')
			stock = request.POST.get('stock')
			weight = request.POST.get('weight')
			offer = request.POST.get('offer')
			discount = request.POST.get('discount')

			Product.objects.filter(id=request.POST.get('id')).update(
				name = name,
				description = des,
				price = price,
				mrp = mrp,
				stock = stock,
				weight = weight,
				offer = offer,
				discount= discount,
				is_active= False
			)
			messages.success(request, 'Product Updated Successfully')
			return redirect('/vendor/product?id='+request.POST.get('id'))
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_delete_product_image(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'GET':
			ProductImages.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_delete_product_variant(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'GET':
			ProductVariant.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_product_out_of_stock(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'GET':
			Product.objects.filter(id=request.GET.get('i')).update(stock=0)
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_orders(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		business_limit = BusinessLimitWallet.objects.get(vendor__user=request.user)
		dic = {
			'orders':SalesOrderItems.objects.filter(store__vendor__user=request.user),
			'vendor':vendor,'business_limit':business_limit,
			'allorder_status':ORDER_STATUS_UPDATE,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_complete_orders(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		dic = {
			'orders':SalesOrderItems.objects.filter(store__vendor__user=request.user),
			'vendor':vendor,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/complete-orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def vendor_order_detail(request):	
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		order_id = request.GET.get('i')
		dic = {
			'vendor':vendor,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		dic.update(get_order_details(order_id))
		return render(request, 'vendor_app/order-detail.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

#changes for COD 
@csrf_exempt
def vendor_change_order_status(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		# admin = User.objects.get(is_superuser = True)
		# print('admin',admin)
		# print(admin.id)
		order_id = request.GET.get('i')
		print(order_id)
		status = request.GET.get('s')
		return_status = request.GET.get('return')
		print(return_status)
		if status == 'Delivered':
			OrderItems.objects.filter(id=order_id).update(delivery_status=status, delivered_on=timezone.now())
			user = OrderItems.objects.get(id=order_id).order.user
			print(user)
			order = OrderItems.objects.get(id=order_id).order
			order_item = OrderItems.objects.filter(id=order_id)
			print(order_item)
			for x in order_item:
				print(x.plan,'LLLLLLLLLLLLLLLLLLLLLLLLLLLL')
				save_pv_transaction(user, x.product, x.subtotal, x.plan)
			if not order.paid:
				orderitems = OrderItems.objects.get(id=order_id)
				admin_commission = (orderitems.total/100)*orderitems.product.category.commission
				print("admin commission percentage")
				print(orderitems.product.category.commission)
				print(admin_commission,'KKKKKKKKKKKKKK')
				gst = (admin_commission/100)*18   #GST of 18 per on admin charge deduct from businesslimit
				print(gst)
				admin_commission_plus_gst = admin_commission + gst
				print("printing total_detection_amt")
				print(admin_commission_plus_gst)
				GST_Log.objects.create(orders = orderitems, gst_amt=gst)
				trans_name = 'Transaction for ORD'+str(order.id)+str(orderitems.id)
				#make_business_limit_transaction(vendor, admin_commission, 'DEBIT', trans_name)
				make_business_limit_transaction(vendor, admin_commission_plus_gst, 'DEBIT', trans_name)
				make_commission_transaction(vendor.user, admin_commission_plus_gst, 'CREDIT')
				user_c = 0.0
				if UserVendorRelation.objects.filter(vendor=vendor).exists():
					print('hhhhhhhhhhhhhhhh')
					user = UserVendorRelation.objects.get(vendor=vendor)
					percentage = float(str(UserVendorCommission.objects.get()))
					user_c = (orderitems.total/100) * percentage
					make_commission_transaction(user, admin_commission_plus_gst, 'CREDIT')
					make_wallet_transaction(vendor.user, user_c, 'DEBIT')
		else:
			OrderItems.objects.filter(id=order_id).update(delivery_status=status)
			notification(vendor.user, 'Order '+status)
		return redirect('/vendor/orderdetail?i='+order_id)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_return_details(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		dic = {
			'orders':SalesOrderItems.objects.filter(store__vendor__user=request.user),
			'vendor':vendor,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/return-order.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt		
def vendor_change_return_status(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		admin = User.objects.get(is_superuser = True)
		order_id = request.GET.get('i')
		return_status = request.GET.get('return')
		print(order_id,return_status)
		if return_status:
			if return_status == "Approved":
				OrderItems.objects.filter(id=order_id).update(return_status=status, return_on=timezone.now())
				user = OrderItems.objects.get(id=order_id).order.user
				print(user)
				order = OrderItems.objects.get(id=order_id).order
				order_item = OrderItems.objects.filter(id=order_id)
				print(order_item)
			else:
				OrderItems.objects.filter(id=order_id).update(return_status=status)
				notification(vendor.user, 'Return '+status)
		return redirect('/vendor/returndetail?i='+order_id)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_brand(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			category = ProductCategory.objects.get(id=request.POST.get('category'))
			name = request.POST.get('name')
			if Brand.objects.filter(category=category, name=name).exists():
				messages.info(request, 'Brand Already Exists')
				return redirect('/vendor/brand')
			else:
				Brand.objects.create(category=category, name=name)
				messages.success(request, 'Brand Added Successfully !!!!')
				return redirect('/vendor/brand')
		else:
			vendor = Vendor.objects.filter(user=request.user)
			dic = {'vendor':vendor, 'categories':ProductCategory.objects.all(),
				'brands':Brand.objects.all(),
				# 'notification':get_notifications(request.user),
				# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'vendor_app/brand.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_payment_transactions(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user)
		dic = {
			'vendor':vendor,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/payment-transactions.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_wallet_dash(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.get(user=request.user)
		if not Wallet.objects.filter(vendor=vendor).exists():
			Wallet.objects.create(vendor=vendor)
		
		wallet = Wallet.objects.get(vendor=vendor)
		transactions = WalletTransaction.objects.filter(wallet=wallet)
		dic = {
			'vendor':vendor,
			'wallet':wallet,
			'transactions':transactions,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/wallet-dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

# Per Product commisson from Admin
@csrf_exempt
def vendor_wallet_commission_dash(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		if not CommissionWallet.objects.filter(vendor=vendor).exists():
			CommissionWallet.objects.create(vendor=vendor,isactive=True)
		wallet_commission = CommissionWallet.objects.filter(vendor=vendor,isactive=True).first()
		
		transactions = CommissionWalletTransaction.objects.filter(commissionwallet=wallet_commission)
		dic = {
			'vendor':vendor,
			'wallet':wallet_commission,
			'transactions':transactions,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/wallet_commission_dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

#method for Business Limit 
@csrf_exempt
def vendor_Business_limit_dash(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.get(user=request.user)
		if not BusinessLimitWallet.objects.filter(vendor=vendor).exists():
			BusinessLimitWallet.objects.create(vendor=vendor)
		
		business_limit = BusinessLimitWallet.objects.get(vendor=vendor)
		business_limit_transactions = BusinessLimitWalletTransaction.objects.filter(businesslimitwallet=business_limit)
		dic = {
			'vendor':vendor,
			'business_limit':business_limit,
			'business_limit_transactions':business_limit_transactions,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/Business-limit-dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_withdraw(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			if float(amount) < 500:
				messages.success(request, 'Withdrawl amount must be greater than 500.')
				return redirect('/vendor/withdraw')
			flag = True
			for x in VendorWithdrawRequest.objects.filter(user=request.user):
				if x.is_active == 0 or x.is_active == 1:
					flag = False
					break
			if flag:
				VendorWithdrawRequest.objects.create(
					user = request.user,
					request_date = timezone.now(),
					amount = amount
				)
				messages.success(request, 'We have received your payment withdraw request. Your payment wil be credited in your account in 3 working days after approval.')
				return redirect('/vendor/withdraw')
			else:
				messages.success(request, 'You already have a withdrawl request pending, please wait for it to credit.')
				return redirect('/vendor/withdraw')
		vendor = Vendor.objects.filter(user=request.user)
		if not Wallet.objects.filter(vendor__user=request.user).exists():
			Wallet.objects.create(vendor__user=request.user)
		dic = {
			'vendor':vendor,
			'wallet':Wallet.objects.filter(vendor__user=request.user).first(),
			'business_limit_wallet':BusinessLimitWallet.objects.filter(vendor__user=request.user).first(),
			'commission_wallet':CommissionWallet.objects.filter(vendor__user=request.user).first(),
			'data':WithdrawRequest.objects.filter(vendor__user=request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/withdraw.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_help(request):
	if check_user_authentication(request, 'VENDOR'):
		user=User.objects.filter(username='admin').first()
		print(user,'UUUUUU')
		if request.method == 'POST':
			subject = request.POST.get('subject')
			message = request.POST.get('message')
			image = request.FILES['image']
			Query.objects.create(user=request.user, query_date=timezone.now(), subject=subject, message=message,image = image)
			messages.success(request, 'Query Received')
			user=User.objects.filter(username='admin').first()
			print(user,'UUUUUU')
			notification(user,'New Query Received')
			return redirect('/vendor/help')
		vendor = Vendor.objects.filter(user=request.user)
		dic = {
			'vendor':vendor,
			'queries':Query.objects.filter(user=request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/help.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

#vender recharge below code not in working
from main_app.razor import *
@csrf_exempt
def vendor_recharge(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			payment_type = request.POST.get('payment_type')
			amount=float(amount)
			amt = float(amount) / 100
			print(amount,amt,payment_type,'AAAAAAAAAAA')
			if payment_type == 'usewallet':
				
				bal=Wallet.objects.filter(user=request.user).first()
				bal_bussiness=BusinessLimitWallet.objects.filter(vendor=request.user.vendor).first()
				if float(amount) >= bal.current_balance:
					messages.warning(request, 'Insufficent balence.')
					return redirect('/vendor/businesslimittransaction')
				else:
					wallet_transactions = WalletTransaction.objects.create(wallet = bal,
					transaction_date = timezone.now(),
					transaction_type = "DEBIT",
					transaction_amount = amount,
					previous_amount = bal.current_balance,
					remaining_amount = bal.current_balance - amount)

					

					Wallet.objects.filter(user=request.user).update(current_balance = bal.current_balance - amount)
					wallet_tans = WalletTransaction.objects.filter(id=wallet_transactions.id).first()
				   
					new_receipt = Recharge_Receipt.objects.create(vendor=request.user.vendor, amount=amount,payment_id='Wallet transactions ID '+str(wallet_tans.id))
					print(new_receipt,'NNNNN')
					receipt = Recharge_Receipt.objects.filter(id=new_receipt.id).first()
					print(receipt.amount,receipt.id,'RRRRRRRRRRRr')
					make_business_limit_transaction(request.user.vendor, receipt.amount, 'CREDIT', 'Recharge Receipt ID  '+str(receipt.id))
					# make_commission_transaction(request.user.vendor, receipt.amount, 'CREDIT')
					sub = 'AVPL - Business Limit Recharged'
					msg = '''Hi there!
							Your business limit has been successfully recharge with amount Rs '''+str(receipt.amount)+'''.

										Thanks!'''
					EmailMessage(sub, msg, to=[request.user.email]).send()
					notification(request.user, 'Recharged Successfully.')
					return render(request, 'vendor_app/recharge-success.html')
								

			else:	
				receipt = Recharge_Receipt.objects.create(vendor=request.user.vendor, amount=amt)
				data = create_razorpay_order(str(receipt.id), request.user.vendor, amount)
				return JsonResponse({'data':data})
		
		else:
			dic = {'business_limit':BusinessLimitWallet.objects.get(vendor=request.user.vendor),
			'bal':Wallet.objects.filter(user=request.user).first(),}
			return render(request, 'vendor_app/businesslimittransaction.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def capture_recharge_payment(request):
	if request.method == 'POST':
		payment_id = request.POST.get('razorpay_payment_id')
		order_id = request.POST.get('razorpay_order_id')
		signature = request.POST.get('razorpay_signature')
		receipt = Recharge_Receipt.objects.get(razorpay_order_id=order_id)
		razorpaytransaction = RazorpayTransaction.objects.create(payment_id=payment_id, order_id=order_id, signature=signature)
		receipt.payment_id = payment_id
		receipt.status = True
		receipt.save()
		make_business_limit_transaction(request.user.vendor, receipt.amount, 'CREDIT', 'Recharge Receipt ID '+str(receipt.id))
		#below vendor recharge amount credit in admin wallet
		make_commission_transaction(request.user.vendor, receipt.amount, 'CREDIT')
		sub = 'AVPL - Business Limit Recharged'
		msg = '''Hi there!
Your business limit has been successfully recharge with amount Rs '''+str(receipt.amount)+'''.

Thanks!'''
		EmailMessage(sub, msg, to=[request.user.email]).send()
		notification(request.user, 'Recharged Successfully.')
		return render(request, 'vendor_app/recharge-success.html')
	else:
		return HttpResponse('Failed')
		
@csrf_exempt
def userSubscriptionRequest(request):
	if request.user.role.level.level=='Vendor':
		if request.method == 'GET':
			data = UserSubscriptionRequest.objects.filter(vendor = request.user.vendor)
			dic={'data':data}
			return render(request, 'vendor_app/subscription-request.html', dic)

from datetime import tzinfo, timedelta, datetime

#function for activate User Subscription
@csrf_exempt
def vendor_activate_subscription(request):
	if check_user_authentication(request, 'VENDOR'):
		id_=request.GET.get('id')
		obj = UserSubscriptionRequest.objects.get(id=id_)
		
		UserSubscriptionRequest.objects.filter(id=id_).update(is_active=True)
		UserData.objects.filter(user=obj.user).update(subscribed=True)
		
		UserSubscription.objects.filter(user = obj.user).delete()
		UserSubscription.objects.create(user = obj.user, months=obj.month)
		
		business_limit=BusinessLimitWallet.objects.get(vendor=request.user.vendor)
		subs_charges = SubscriptionCharge.objects.get()
		amount = obj.amount
		Gst = (amount/100)*18
		amt = amount -Gst
		vendor_percentage = subs_charges.vendor_percentage
		comiission_vendor = (amt/100)*float(vendor_percentage)
		admin_amt = float(amt) - float(comiission_vendor)
		admin_amt = float(admin_amt) + float(Gst)
		make_business_limit_transaction(request.user.vendor, admin_amt, 'DEBIT', 'payment sucessfull')
		make_commission_transaction(obj.user ,admin_amt, 'CREDIT')
		node = MLM.objects.get(node = obj.user)
		if not node.parent.role.level.level == 'Admin':
			save_pv_transaction2(node.parent, float(amount), 'Level')
		sub = 'Online Aap Ki Apni Dukaan - Subscription Activated Successfully'
		msg = '''Hi '''+obj.user.usr.first_name+'''!

You have successfully subscribed to Plus Membership of Online Aap Ki Apni Dukaan. Now you will get free delivery for 1 year. Enjoy shopping on onlineapnidukaan.com

Thanks & Regards,
Team Online Aap Ki Apni Dukaan'''
		EmailMessage(sub,msg,to=[obj.user.email]).send()
		messages.success(request, 'User Subscription Activated Successfully !!!!')
		notification(request.user, 'Vendor '+obj.vendor.first_name+' '+obj.vendor.last_name)
		notification(obj.user, 'Subscription Activated Successfully.')
		return redirect('/vendor/userSubscriptionRequest')
	else:
		return HttpResponse('404 Not Found')

@csrf_exempt
def vendor_billing_requests(request):
	if check_user_authentication(request, 'VENDOR'):
		dic = {'requests':Billing_Request.objects.filter(store=request.user.vendor.store, is_active=False)}
		return render(request, 'vendor_app/billing-requests.html', dic)
	return HttpResponse('404 Not Found')
@csrf_exempt
def vendor_confirm_billing_requests(request):
	if check_user_authentication(request, 'VENDOR'):
		config = None
		if len(Billing_Config.objects.all()) > 0:
			config = Billing_Config.objects.get()
		else:
			messages.success(request, 'Billing request not configured by admin yet')
			return redirect('/vendor/billing/requests/')
		billing = Billing_Request.objects.get(id=request.GET.get('i'))
		check_user_subscription(billing.user)
		admin_commission = save_vendor_commission(request.user, billing.amount, config.admin_commission)
		make_business_limit_transaction(billing.store.vendor, admin_commission, 'DEBIT', 'Billing Request Approval')
		user_c = 0.0
		if UserVendorRelation.objects.filter(vendor=billing.store.vendor).exists():
			user = UserVendorRelation.objects.get(vendor=billing.store.vendor)
			percentage = float(str(UserVendorCommission.objects.get()))
			user_c = (billing.amount/100) * percentage
			make_wallet_transaction(billing.user, user_c, 'CREDIT')
			make_business_limit_transaction(billing.store.vendor, user_c, 'DEBIT', 'User Commission')
			#make_wallet_transaction(billing.store.vendor.user, user_c, 'DEBIT')
		pv_percent = config.pv_percent
		pv = (billing.amount/100)*pv_percent
		total_pv = billing.user.usr.pv + pv
		PVTransactions.objects.create(
			user = billing.user,
			transaction_date = timezone.now(),
			previous_pv = billing.user.usr.pv,
			pv = pv,
			total_pv = billing.user.usr.pv + pv,
			plan = billing.plan
		)
		update_user_pv(billing.user, pv, billing.plan)
		billing.status = True
		billing.save()
		msg = ''' Hi there!
Your billing request has been approved by the vendor successfully. We have also transacted the resulted PV in your wallet.

Thanks!'''
		EmailMessage('AVPL - Billing Requests Approved', msg, to=[billing.user.email]).send()
		messages.success(request, 'Billing Request Approved Successfully')
		return redirect('/vendor/billing/requests/')
	return HttpResponse('404 Not Found')




####################################################################################################################################





from django.contrib.auth.decorators import login_required
# from main_app.models import Wallet,WalletTransfer
import random
from django.db import transaction
import datetime


login_required('/')
@csrf_exempt
def vendorbalanacetransfer(request):
	bal = Wallet.objects.get(vendor__user=request.user).currentbalance
	transectiondata = WalletTransfer.objects.filter(user=request.user).order_by('-id')
	context = {
			
			'transectiodetails':transectiondata,
			'bal':bal,# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}

	id = WalletTransferApproval.objects.all()[0:1]

	if id is not None:

		for id in id:

			print(id.id,'idddd')

	if WalletTransferApproval.objects.get(id =id.id).vendor == 1 :

		if request.method == 'POST':
			print(request.user)
			request.session['recivername'] = request.POST.get('rvname') 
			request.session['amount']  = int(request.POST.get('amt'))
			request.session['senderotp'] = random.randint(100000,999999)
			request.session['timer'] = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
			print(request.session['timer'])

			# print('-------------------------->',request.session['recivername'],request.session['senderotp'],type(request.session['timer']))
			print(request.session['senderotp'],'\n---------->',request.session['recivername'])
			msg = ''' Hi there!
Your OTP for wallet transfer for sending ₹''' + str(request.session['amount']) +''' to ''' + request.session['recivername']+ '''is ''' + str(request.session['senderotp'])+'''.

Thanks!'''
			EmailMessage('AVPL - OTP for Wallet transfer', msg, to=[request.user.email]).send()
			print(request.user.email)
			messages.success(request, 'OTP sent successfully.')
			return render(request,'vendor_app/otpverify.html')
		return render(request,'vendor_app/customerwallettransfer.html',context=context)
	else :
		messages.error(request,'Payments Mode off')
		return render(request,'vendor_app/customerwallettransfer.html',context=context)




login_required('/')
@csrf_exempt
@transaction.atomic
def transfer_amount_vendor(request):
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
		print(senderotp)
		# reciverotp = int(request.POST.get('otp2') )
		# print(datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f'))

		# if datetime.datetime.now() < datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f') :
		
			# if senderotp == request.session['senderotp'] and reciverotp == request.session['reciverotp']:
		if senderotp == request.session['senderotp']:
			print('hjhjjjjjjjjjjjj')
			if Wallet.objects.get(user=request.user).current_balance >= request.session['amount']:
				print('LLLLLLLLLLLLLLLLLLL')
				make_wallet_transaction(user = request.user, amount = request.session['amount'], trans_type = 'DEBIT')
				make_wallet_transaction(user = User.objects.get(username = request.session['recivername']), 
					amount = request.session['amount'], trans_type = 'CREDIT')
				print(request.session['recivername'])
				transfer_into_another_account(usr = request.user, sender = request.user.username,
					reciver = request.session['recivername'],amount = request.session['amount'])
				print('done')
				messages.success(request,'Successfully Transfered')
				return redirect('balanacetransfer')


			else :
				messages.error(request,'Not having sufficient balance')
				return redirect('balanacetransfer')

		else :
			messages.error(request,'OTP is not Correct')
			return redirect('otpvalidation')
		# else:
		# 	messages.error(request,'Timeout')
		# 	return redirect('balanacetransfer')
	return render(request,'vendor_app/otpverify.html')
	# return render(request,'user_app/otpverify.html')









