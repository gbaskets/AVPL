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
from purchase_app.models import *
from vendor_app.models import *
from main_app.models import *
from admin_app.models import *
from django.http import JsonResponse
from vendor_app.utils import *
from accountant_app.models import *
from main_app.utils import *
from django.utils import timezone

ORDER_STATUS_UPDATE = (
    ("Pending", "Pending"),
    ("Order Placed", "Order Placed"),
    ("Packed", "Packed"),
    ("Shipped", "Shipped"),
    # ("Delivered", "Delivered"),
    
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
                
				storeobj=Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
    
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
				
							
				dic = {'vendor':vendor, 'storeobj':Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first(),
				'allorder_status':ORDER_STATUS_UPDATE,'wallet':wallet,
                'business_limit':business_limit,
                'wallet_commission':wallet_commission,
				'business_limit_transactions':business_limit_transactions,
				'transactions':transactions,
                 'salesorder': SalesOrder.objects.filter(store=storeobj).order_by("-id"),
                 'salesorder': SalesOrder.objects.filter(store=storeobj).order_by("-id"),
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
    
	vendor = Vendor.objects.filter(user=request.user).first()
	storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		
	if request.method == "POST":
		order_id = request.POST.get('order_id')
		order = SalesOrder.objects.filter(id=order_id).first()
		delivery_status=request.POST.get('delivery_status')
		if order.ispaymentpaid == False :
			if SalesOrderItems .objects.filter(salesorder=order).exists():
				for salesitem in SalesOrderItems .objects.filter(salesorder=order).all():
					TaxLog.objects.create(transactiondate=timezone.now(),salesorderitems = salesitem, taxamount=salesitem.tax)
			order.ispaymentpaid=True
			order.save()
			make_business_limit_transaction("VENDOR",request.user,order.total, 'DEBIT')
		
		
		if SalesOrderItems .objects.filter(salesorder=order).exists():
			if delivery_status == 'Delivered':
				admin=User.objects.filter(username="admin").first()
				make_commission_transaction('ADMIN',admin, order.totaladmincommission, 'CREDIT')
				SalesOrderItems .objects.filter(salesorder=order).update(orderstatus=delivery_status, deliveredon=timezone.now())
			else:
				SalesOrderItems .objects.filter(salesorder=order).update(orderstatus=delivery_status)
		messages.success(
			request, f"The order status of order_id ORD{order_id} has been updated ! ")
				
			# for x in order_item:
			# 	print(x.plan,'LLLLLLLLLLLLLLLLLLLLLLLLLLLL')
			# 	save_pv_transaction(user, x.product, x.subtotal, x.plan)
			# if not order.paid:
			# 	orderitems = OrderItems.objects.filter(order=order_id).first()
			# 	print(orderitems,'OOOOOOOOO')
			# 	admin_commission = (orderitems.total/100)*orderitems.product.category.commission
			# 	print("admin commission percentage")
			# 	print(orderitems.product.category.commission)
			# 	print(admin_commission,'KKKKKKKKKKKKKK')
			# 	gst = (admin_commission/100)*18   #GST of 18 per on admin charge deduct from businesslimit
			# 	print(gst)
			# 	admin_commission_plus_gst = admin_commission + gst
			# 	print("printing total_detection_amt")
			# 	print(admin_commission_plus_gst)
			# 	TaxLog.objects.create(transactiondate=timezone.now(),salesorderitems = orderitems, taxamount=gst)
			# 	trans_name = 'Transaction for ORD'+str(order.id)+str(orderitems.id)
			# 	#make_business_limit_transaction(vendor, admin_commission, 'DEBIT', trans_name)
			# 	make_business_limit_transaction(vendor, admin_commission_plus_gst, 'DEBIT', trans_name)
			# 	make_commission_transaction(vendor.user, admin_commission_plus_gst, 'CREDIT')
			# 	user_c = 0.0
			# 	if UserVendorRelation.objects.filter(vendor=vendor).exists():
			# 		print('hhhhhhhhhhhhhhhh')
			# 		user = UserVendorRelation.objects.get(vendor=vendor)
			# 		percentage = float(str(UserVendorCommission.objects.get()))
			# 		user_c = (orderitems.total/100) * percentage
			# 		make_commission_transaction(user, admin_commission_plus_gst, 'CREDIT')
			# 		make_wallet_transaction(vendor.user, user_c, 'DEBIT')
		
			# orderitem= OrderItems.objects.filter(order=order_id)
			# print(orderitem,'oitem')
			# for item in orderitem:  
			# 	item.delivery_status = delivery_status 
			# 	item.save()
		
	return redirect('/vendor')



@csrf_exempt
def Store_list(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.get(user=request.user)
		businessmaincategory_obj=BusinessMainCategory.objects.filter(isactive=True)
		businesscategory_obj=BusinessCategory.objects.filter(isactive=True)
		
		if Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).exists():
			storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		else:
			storeobj=""
		dic={"businessmaincategory_obj":businessmaincategory_obj,
				"businesscategory_obj":businesscategory_obj,
				"storeobj":storeobj,
                'store_list':Store.objects.filter(vendor=vendor)
				}	

		return render(request, 'vendor_app/store/store-list.html',dic )
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def Store_Selected_List(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.get(user=request.user)	
		if request.method == 'POST':
			vendor = Vendor.objects.get(user=request.user)
			storeid = request.POST.get('storeid')
			isselectedcurrentstore = request.POST.get('isselectedcurrentstore')
			print(isselectedcurrentstore,storeid,'isselectedcurrentstore')
			if storeid and isselectedcurrentstore :
				Store.objects.filter(vendor=vendor).update(isselectedcurrentstore=False)
				Store.objects.filter(vendor=vendor,id=storeid).update(isselectedcurrentstore=True)
			else:
				pass
		else:
			pass
  
		return redirect("/vendor/store")
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





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
				storeobj=Store.objects.create(vendor = vendor,storename=storename,isselectedcurrentstore=True)
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
				storeobj.isselectedcurrentstore=True
				storeobj.save()
			else:
				storeobj=Store.objects.filter(vendor = vendor,storename=storename,isselectedcurrentstore=True).first()
			    
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
			storeobj.isselectedcurrentstore=True
			storeobj.save()
			
			Vendor.objects.filter(id=vendor.id).update(storecreated=True,docsubmitted=True)
			messages.info(request, 'Store Created Successfully !!!!')
			return redirect('/vendor/')
		businessmaincategory_obj=BusinessMainCategory.objects.filter(isactive=True)
		businesscategory_obj=BusinessCategory.objects.filter(isactive=True)
        
		if Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).exists():
			storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		else:
			storeobj=""
		dic={"businessmaincategory_obj":businessmaincategory_obj,
				"businesscategory_obj":businesscategory_obj,
                 "storeobj":storeobj,
				}
		return render(request, 'vendor_app/store/store-register.html',dic )
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def add_new_store(request):
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
				return redirect('/vendor/store')
			else:
				messages.info(request, 'Already storename is exits !!!')
				return redirect('/vendor/store')
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

			return render(request, 'vendor_app/store/vendor-doc.html', dic)
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
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {
			'vendor':vendor,'storeobj':storeobj,
			'categories':ProductCategory.objects.all(),
			'subcategories':ProductSubCategory.objects.all(),
			'subsubcategories':ProductSubSubCategory.objects.all(),
            'units':Unit.objects.all(),
			'brands':Brand.objects.all(),
			'products':Product.objects.filter(store=storeobj),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product/product-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def add_product(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == 'POST':
		
			unit_id=request.POST.get('unit_id') 
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
	
			if Product.objects.filter(store=storeobj, productname=productname).exists():
				messages.info(request, f'Product: {productname} is already exits !')
				return redirect('/vendor/product-list')
			else:
				if productname and category_id :				
					pro = Product.objects.create(store = storeobj,productname = productname,description = description)
					if category_id:
						pro.category = ProductCategory.objects.get(id=category_id)
					if subcategory_id:
						pro.subcategory = ProductSubCategory.objects.get(id=subcategory_id)
					if subsubcategory_id:
						pro.subsubcategory = ProductSubSubCategory.objects.get(id=subsubcategory_id)
					if brand_id:
						pro.brand = Brand.objects.get(id=brand_id)
					if unit_id:
						pro.unit = Unit.objects.get(id=unit_id)
      
					if hsn:
						pro.hsn= hsn
					if tax:
						pro.tax= tax
					if pv:
						pro.pv =pv
					if admincommission:
						pro.admincommission =admincommission
                    
				
					pro.updatedby= request.user
					pro.save()
					messages.success(request,f'Product {productname} is Added Successfully')
					return redirect('/vendor/product-list')
				else:
					messages.info(request, f'Please fill all detials such as productname and category !')
					return redirect('/vendor/product-list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def edit_product(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == 'POST':

			category_id=request.POST.get('category_id') 
			subcategory_id=request.POST.get('subcategory_id') 
			subsubcategory_id=request.POST.get('subsubcategory_id') 
			brand_id=request.POST.get('brand_id') 
			unit_id=request.POST.get('unit_id') 
			productname=request.POST.get('productname') 
			description=request.POST.get('description') 
			hsn=request.POST.get('hsn') 
			tax=request.POST.get('tax') 
			pv=request.POST.get('pv') 
			admincommission=request.POST.get('admincommission') 
	
			if Product.objects.filter(id=id).exists():
				pro=Product.objects.filter(id=id).first()
				
				if productname :
					pro.productname = productname
				if description:
					pro.description = description
					
				if category_id:
					pro.category = ProductCategory.objects.get(id=category_id)
				if subcategory_id:
					pro.subcategory = ProductSubCategory.objects.get(id=subcategory_id)
				if subsubcategory_id:
					pro.subsubcategory = ProductSubSubCategory.objects.get(id=subsubcategory_id)
				if brand_id:
					pro.brand = Brand.objects.get(id=brand_id)
				if unit_id:
					pro.unit = Unit.objects.get(id=unit_id)
				if hsn:
					pro.hsn= hsn
				if tax:
					pro.tax= tax
				if pv:
					pro.pv =pv
				if admincommission:
					pro.admincommission =admincommission

				pro.updatedby= request.user
				pro.save()
				messages.success(request,f'Product {productname} is updated Successfully')
				return redirect('/vendor/product-list')
			else:
				messages.info(request, f'Please fill all detials such as productname and category !')
				return redirect('/vendor/product-list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

		

@csrf_exempt
def vendor_product_variants_all_list(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj=Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {
			'vendor':vendor,'storeobj':storeobj,
			'categories':ProductCategory.objects.filter(),
			'subcategories':ProductSubCategory.objects.filter(),
			'subsubcategories':ProductSubSubCategory.objects.filter(),
            'units':Unit.objects.filter(),
			'brands':Brand.objects.filter(),
            'product_variants':ProductVariants.objects.filter(store=storeobj),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product/product-variants-all-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def vendor_product_variants_list(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj=Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		productobj=Product.objects.filter(store=storeobj,id=id).first()
		dic = {
			'vendor':vendor,'storeobj':storeobj,
			'categories':ProductCategory.objects.filter(),
			'subcategories':ProductSubCategory.objects.filter(),
			'subsubcategories':ProductSubSubCategory.objects.filter(),
            'units':Unit.objects.filter(),
			'brands':Brand.objects.filter(),
			'firstvariantvalue':FirstVariantValue.objects.filter(firstvariant__category__id=productobj.category.id),
			'secondvariantvalue':SecondVariantValue.objects.filter(secondvariant__category__id=productobj.category.id),
			'thirdvariantvalue':ThirdVariantValue.objects.filter(thirdvariant__category__id=productobj.category.id),
			'products':Product.objects.filter(store=storeobj,id=id).first(),
            'product_variants':ProductVariants.objects.filter(store=storeobj,product__id=id),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product/product-variants-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def add_product_variants(request,id):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'POST':
			vendor = Vendor.objects.filter(user=request.user).first()
			storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
			product_id=id 
			firstvariantvalue_id=request.POST.get('firstvariantvalue_id') 
			secondvariantvalue_id=request.POST.get('secondvariantvalue_id') 
			thirdvariantvalue_id=request.POST.get('thirdvariantvalue_id') 
			productvariantname=request.POST.get('productvariantname') 
			productimage=request.FILES.get('productimage') 
			quantity=request.POST.get('quantity') 
			mrp=request.POST.get('mrp') 
			purchaseprice=request.POST.get('purchaseprice') 
			price=request.POST.get('price') 
	
			if ProductVariants.objects.filter(store=storeobj, productvariantname=productvariantname).exists():
				messages.info(request, f'Product Variant: {productvariantname} is already exits !')
				return redirect(f'/vendor/product-variants-list/{product_id}')
			else:
				if product_id  and productvariantname and productimage:
					product = Product.objects.filter(store=storeobj, id=id).first()
					productvariantsobj=ProductVariants.objects.create(store=storeobj,product=product, productvariantname=productvariantname,productimage=productimage)        
					productvariantsobj.sku=generate_code(productvariantsobj.id,[product.productname,product.category.name,product.brand.name])
					productvariantsobj.upc=generate_bracode("")[1]
					productvariantsobj.barcodeimage.save(f'{productvariantname}.png',generate_bracode("")[0])
				
					if firstvariantvalue_id:
						productvariantsobj.firstvariantvalue = FirstVariantValue.objects.get(id=firstvariantvalue_id.split(",")[0])
					if secondvariantvalue_id:
						productvariantsobj.secondvariantvalue = SecondVariantValue.objects.get(id=secondvariantvalue_id.split(",")[0])
					if thirdvariantvalue_id:
						productvariantsobj.thirdvariantvalue = ThirdVariantValue.objects.get(id=thirdvariantvalue_id.split(",")[0])
					
					if quantity:
						productvariantsobj.quantity = int(quantity)
      
					if mrp:
						productvariantsobj.mrp= float(mrp)
					if purchaseprice:
						productvariantsobj.purchaseprice= float(purchaseprice)
					if price:
						productvariantsobj.price =float(price)
					
					productvariantsobj.updatedby= request.user
					productvariantsobj.save()
					messages.success(request,f'Product Variants {productvariantname} is Added Successfully')
					return redirect(f'/vendor/product-variants-list/{product_id}')
				else:
					messages.info(request, f'Please fill all detials such as productvariantname and price !')
					return redirect(f'/vendor/product-variants-list/{product_id}')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def edit_product_variants(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == 'POST':

			firstvariantvalue_id=request.POST.get('firstvariantvalue_id') 
			secondvariantvalue_id=request.POST.get('secondvariantvalue_id') 
			thirdvariantvalue_id=request.POST.get('thirdvariantvalue_id') 
			productvariantname=request.POST.get('productvariantname') 
			productimage=request.FILES.get('productimage') 
			quantity=request.POST.get('quantity') 
			mrp=request.POST.get('mrp') 
			purchaseprice=request.POST.get('purchaseprice') 
			price=request.POST.get('price') 
			ispublished=request.POST.get('ispublished')
			print(ispublished,'ispublished')

			if ProductVariants.objects.filter(store=storeobj,id=id).exists():
				productvariantsobj=ProductVariants.objects.filter(store=storeobj,id=id).first()
	
				if productvariantname :
					productvariantsobj.productvariantname=productvariantname
	    
				if productimage:
					productvariantsobj.productimage=productimage
					
				if firstvariantvalue_id:
					productvariantsobj.firstvariantvalue = FirstVariantValue.objects.get(id=firstvariantvalue_id.split(",")[0])
				if secondvariantvalue_id:
					productvariantsobj.secondvariantvalue = SecondVariantValue.objects.get(id=secondvariantvalue_id.split(",")[0])
				if thirdvariantvalue_id:
					productvariantsobj.thirdvariantvalue = ThirdVariantValue.objects.get(id=thirdvariantvalue_id.split(",")[0])
				
				if quantity:
					productvariantsobj.quantity = int(quantity)
	
				if mrp:
					productvariantsobj.mrp= float(mrp)
				if purchaseprice:
					productvariantsobj.purchaseprice= float(purchaseprice)
				if price:
					productvariantsobj.price =float(price)
				productobj=Product.objects.filter(id=productvariantsobj.product.id).first()
				if ispublished :
					productvariantsobj.ispublished=True
					productobj.ispublished=True
				else:
					productvariantsobj.ispublished=False
					productobj.ispublished=False
				
				productvariantsobj.updatedby= request.user
				productobj.save()
				productvariantsobj.save()
				messages.success(request,f'Product Variants {productvariantname} is updated Successfully')
				return redirect(f'/vendor/product-variants-list/{productvariantsobj.product.id}')
			else:
				pass
		
		dic = {
			'vendor':vendor,'storeobj':storeobj,
			'categories':ProductCategory.objects.filter(),
			'subcategories':ProductSubCategory.objects.filter(),
			'subsubcategories':ProductSubSubCategory.objects.filter(),
			'units':Unit.objects.filter(),
			'brands':Brand.objects.filter(),
			'firstvariantvalue':FirstVariantValue.objects.filter(firstvariant__category__id=id),
			'secondvariantvalue':SecondVariantValue.objects.filter(secondvariant__category__id=id),
			'thirdvariantvalue':ThirdVariantValue.objects.filter(thirdvariant__category__id=id),
			'products':Product.objects.filter(store=storeobj,id=id).first(),
			'product_variants':ProductVariants.objects.filter(store=storeobj,product__id=id),
			# 'notification':get_notifications(request.user)
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product/product-variants-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def delete_product_variants(request,pk,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		productvariantsobj=ProductVariants.objects.filter(store=storeobj,id=id).delete()
		messages.success(request,f'Product Variants is deleted Successfully')
		return redirect(f'/vendor/product-variants-list/{pk}')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





@csrf_exempt
def vendor_profile(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		businessmaincategory_obj=BusinessMainCategory.objects.filter(isactive=True)
		businesscategory_obj=BusinessCategory.objects.filter(isactive=True)
		
		
	
		dic = {
			'storeobj':storeobj,
			'vendor':vendor,
            "businessmaincategory_obj":businessmaincategory_obj,
			"businesscategory_obj":businesscategory_obj,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}			
		return render(request,'vendor_app/store/vendor-profile.html', dic)
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


			
			
			storeobj=Store.objects.filter(vendor=vendor_obj,isselectedcurrentstore=True).first()
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
def vendor_delete_product_image(request):
	if check_user_authentication(request, 'VENDOR'):
		if request.method == 'GET':
			ProductImages.objects.filter(id=request.GET.get('i')).delete()
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
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		business_limit = BusinessLimitWallet.objects.get(vendor__user=request.user)
		dic = {
			'salesorder': SalesOrder.objects.filter(store=storeobj).order_by("-id"),
			'notification_len':len(Notification.objects.filter(vendor=vendor, isread=False)),
			'business_limit':business_limit,'storeobj':storeobj,
			'salesorder': SalesOrder.objects.filter(store=storeobj).order_by("-id"),
			'notification_len':len(Notification.objects.filter(vendor=vendor, isread=False)),
			'business_limit':business_limit,
			'allorder_status':ORDER_STATUS_UPDATE,
			# 'notification':get_notifications(request.user),
		}
		return render(request, 'vendor_app/order_app/orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def vendor_purchases(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		business_limit = BusinessLimitWallet.objects.get(vendor__user=request.user)
		dic = {
			'purchasesorder': PurchasesOrder.objects.filter(store=storeobj).order_by("-id"),
			'notification_len':len(Notification.objects.filter(vendor=vendor, isread=False)),
			'business_limit':business_limit,'storeobj':storeobj,
			'purchasesorder': PurchasesOrder.objects.filter(store=storeobj).order_by("-id"),
			'notification_len':len(Notification.objects.filter(vendor=vendor, isread=False)),
			'business_limit':business_limit,
			'allorder_status':ORDER_STATUS_UPDATE,
			# 'notification':get_notifications(request.user),
		}
		return render(request, 'vendor_app/order_app/purchases_orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def vendor_order_detail(request):	
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		order_id = request.GET.get('i')
		dic = {
			'vendor':vendor,'storeobj':storeobj,
            "salesorder":SalesOrder.objects.filter(id=order_id).first()
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		
		return render(request, 'vendor_app/order_app/order-detail.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_return_details(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {
			'orders':SalesOrderItems.objects.filter(store=storeobj),
			'vendor':vendor,'storeobj':storeobj,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/return-order.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt		
def vendor_change_return_status(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
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
def vendor_payment_transactions(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {
			'vendor':vendor,'storeobj':storeobj,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/payment-transactions.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def vendor_wallet_dash(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if not Wallet.objects.filter(vendor=vendor).exists():
			Wallet.objects.create(vendor=vendor)
		
		wallet = Wallet.objects.get(vendor=vendor)
		transactions = WalletTransaction.objects.filter(wallet=wallet).order_by("-transactiondate")
		dic = {
			'vendor':vendor,"storeobj":storeobj,
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
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if not CommissionWallet.objects.filter(vendor=vendor).exists():
			CommissionWallet.objects.create(vendor=vendor,isactive=True)
		wallet_commission = CommissionWallet.objects.filter(vendor=vendor,isactive=True).first()
		
		transactions = CommissionWalletTransaction.objects.filter(commissionwallet=wallet_commission)
		dic = {
			'vendor':vendor,'storeobj':storeobj,
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
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if not BusinessLimitWallet.objects.filter(vendor=vendor).exists():
			BusinessLimitWallet.objects.create(vendor=vendor)
		
		business_limit = BusinessLimitWallet.objects.get(vendor=vendor)
		business_limit_transactions = BusinessLimitWalletTransaction.objects.filter(businesslimitwallet=business_limit)
		dic = {
			'vendor':vendor,"storeobj":storeobj,
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
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == 'POST':
			amount = request.POST.get('amount')
			if float(amount) < 500:
				messages.success(request, 'Withdrawl amount must be greater than 500.')
				return redirect('/vendor/withdraw')
			if not Wallet.objects.filter(vendor__user=request.user).first().currentbalance >= float(amount) :
				messages.success(request, 'Insufficient balance !')
				return redirect('/vendor/withdraw')
                
			flag = True
			for x in WithdrawRequest.objects.filter(vendor=vendor):
				if x.isactive == 0 or x.isactive == 1:
					flag = False
					break
        
			if flag:
				WithdrawRequest.objects.create(
					vendor=vendor,
					requestdate = timezone.now(),
					amount = amount
				)
				messages.success(request, 'We have received your payment withdraw request. Your payment wil be credited in your account in 3 working days after approval.')
				return redirect('/vendor/withdraw')
			else:
				messages.success(request, 'You already have a withdrawl request pending, please wait for it to credit.')
				return redirect('/vendor/withdraw')
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if not Wallet.objects.filter(vendor__user=request.user).exists():
			Wallet.objects.create(vendor__user=request.user,)
		dic = {
			'vendor':vendor,"storeobj":storeobj,
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
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == 'POST':
			amount = request.POST.get('amount')
			payment_type = request.POST.get('payment_type')
			amount=float(amount)
			amt = float(amount) / 100
			print(amount,amt,payment_type,'AAAAAAAAAAA')
			if payment_type == 'usewallet':
				
				bal=Wallet.objects.filter(vendor__user=request.user).first()
				bal_bussiness=BusinessLimitWallet.objects.filter(vendor__user=request.user).first()
				if float(amount) >= bal.currentbalance:
					messages.warning(request, 'Insufficent balence.')
					return redirect('/vendor/businesslimittransaction')
				else:
					wallet_transactions = WalletTransaction.objects.create(wallet = bal,
					transactiondate = timezone.now(),
					transactiontype = "DEBIT",
					transactionamount = amount,
					previousamount = bal.currentbalance,
					remainingamount = bal.currentbalance - amount)					

					bal.currentbalance = bal.currentbalance - amount
					bal.save()
					wallet_tans = WalletTransaction.objects.filter(id=wallet_transactions.id).first()
					paymenttransactionobj=PaymentTransaction()
					paymenttransactionobj.vendor = vendor
					paymenttransactionobj.paymentgatway="Wallet"
					paymenttransactionobj.transactionid =wallet_transactions.id
					paymenttransactionobj.transactionrealted= 'Recharge-BusinessLimitWallet'
					paymenttransactionobj.transactiondetails = 'Wallet transactions ID '+str(wallet_tans.id)
					paymenttransactionobj.amount = amount
			
					paymenttransactionobj.save()
     
					print(paymenttransactionobj,'NNNNN')
					
			
					make_business_limit_transaction('VENDOR',request.user, amount, 'CREDIT')
					# make_commission_transaction(request.user.vendor, receipt.amount, 'CREDIT')
					sub = 'AVPL - Business Limit Recharged'
					msg = '''Hi there!
							Your business limit has been successfully recharge with amount Rs '''+str(paymenttransactionobj.amount)+'''.

										Thanks!'''
					EmailMessage(sub, msg, to=[request.user.email]).send()
					# notification(request.user, 'Recharged Successfully.')
					return render(request, 'vendor_app/recharge-success.html')
								

			else:	
				receipt = PaymentTransaction.objects.create(vendor__user=request.user, amount=amt)
				data = create_razorpay_order(str(receipt.id), request.user.vendor, amount)
				return JsonResponse({'data':data})
		
		else:
			dic = {'business_limit':BusinessLimitWallet.objects.get(vendor__user=request.user),
			'bal':Wallet.objects.filter(vendor__user=request.user).first(),
              "storeobj":storeobj}
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
		
		business_limit=BusinessLimitWallet.objects.get(vendor__user=request.user)
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
		dic = {'requests':BillingRequest.objects.filter(store=request.user.vendor.store, is_active=False)}
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
	vendor = Vendor.objects.filter(user=request.user).first()
	storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
	bal = Wallet.objects.get(vendor__user=request.user).currentbalance
	transectiondata = WalletBalanceTransfer.objects.filter(sender=request.user.username).order_by('-id')
	context = {
			'wallet':Wallet.objects.filter(vendor__user=request.user).first(),"storeobj":storeobj,
			'business_limit_wallet':BusinessLimitWallet.objects.filter(vendor__user=request.user).first(),
			'commission_wallet':CommissionWallet.objects.filter(vendor__user=request.user).first(),
			'transectiodetails':transectiondata,'userlist':User.objects.filter(is_active=True).exclude(id=request.user.id),
			'bal':bal,# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}

	if WalletTransferApprovalSettings.objects.filter().first().vendor == True :

		if request.method == 'POST':
			print(request.user,'dattransfer')
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
		print('Payments Mode off')
		return render(request,'vendor_app/customerwallettransfer.html',context=context)



login_required('/')
@csrf_exempt
def vendorselfbalanacetransfer(request):
	vendor = Vendor.objects.filter(user=request.user).first()
	storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
	bal = Wallet.objects.get(vendor__user=request.user).currentbalance
	transectiondata = WalletBalanceTransfer.objects.filter(sender=request.user.username).order_by('-id')
	context = {
			'wallet':Wallet.objects.filter(vendor__user=request.user).first(),"storeobj":storeobj,
			'business_limit_wallet':BusinessLimitWallet.objects.filter(vendor__user=request.user).first(),
			'commission_wallet':CommissionWallet.objects.filter(vendor__user=request.user).first(),
			'transectiodetails':transectiondata,'userlist':User.objects.filter(is_active=True).exclude(id=request.user.id),
			'bal':bal,# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}

	if WalletTransferApprovalSettings.objects.filter().first().vendor == True :

		if request.method == 'POST':
			print(request.user,'dattransfer')
			balance_from = request.POST.get('balance_from') 
			amt  = int(request.POST.get('amt'))
			if balance_from == "businesslimit" :
				business_limit_wallet =BusinessLimitWallet.objects.filter(vendor__user=request.user).first()
				if business_limit_wallet.currentbalance >= amt :
					transactionid=reference_no_transaction("VENDOR",request.user)
					transactiondetails=f'Withdraw Amount Rs.{amt} /- from BusinessLimitWallet - {request.user.username}'
					make_business_limit_transaction("VENDOR",request.user, amt,'DEBIT',transactionid,'BALANCETRANSFER',transactiondetails)
					make_wallet_transaction("VENDOR",request.user, amt, 'CREDIT',transactionid,'BALANCETRANSFER',transactiondetails)
					
					messages.success(request, 'Payment transfer has been successfully !')
					return redirect("/vendor/balanacetransfer")
				else:
					messages.error(request,'Insufficient Balance !')
					return render(request,'vendor_app/customerwallettransfer.html',context=context)
	
			elif balance_from == "commission" :
				commission_wallet=CommissionWallet.objects.filter(vendor__user=request.user).first()
				if commission_wallet.currentbalance >= amt :
					make_commission_transaction("VENDOR",request.user, amt,'DEBIT')
					make_wallet_transaction("VENDOR",request.user, amt,'CREDIT')
					messages.success(request, 'Payment transfer has been successfully !')
					return redirect("/vendor/balanacetransfer")
				else:
					messages.error(request,'Insufficient Balance !')
					return render(request,'vendor_app/customerwallettransfer.html',context=context)
			else:
				messages.error(request,'Please select balance transfer from !')
				return render(request,'vendor_app/customerwallettransfer.html',context=context)
		return render(request,'vendor_app/customerwallettransfer.html',context=context)
	else :
		messages.error(request,'Payments Mode off')
		print('Payments Mode off')
		return render(request,'vendor_app/customerwallettransfer.html',context=context)



login_required('/')
@csrf_exempt
@transaction.atomic
def transfer_amount_vendor(request):
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
		print(senderotp)
		
		if senderotp == request.session['senderotp']:
			print('hjhjjjjjjjjjjjj')
			if Wallet.objects.get(vendor__user=request.user).currentbalance >= request.session['amount']:
				print('LLLLLLLLLLLLLLLLLLL')

				transactionid=reference_no_transaction('ADMIN',request.user)
				transactionrealted= "BALANCE-TRANSAFER",
				transactiondetails = f"Balance transafer Rs.{request.session['amount']}/- by {request.user.username} to {request.session['recivername']}"

				make_wallet_transaction("VENDOR",request.user, request.session['amount'],'DEBIT',transactionid,transactionrealted,transactiondetails)
	
    
				reciveruser=User.objects.get(username = request.session['recivername'])
				if reciveruser.groups.filter(name="ADMIN"):
					group_name="ADMIN"   
				elif reciveruser.groups.filter(name="VENDOR"):
					group_name="VENDOR"  
				elif reciveruser.groups.filter(name="CUSTOMER"):
						group_name="CUSTOMER"  
				make_wallet_transaction(group_name,User.objects.get(username = request.session['recivername']), 
					request.session['amount'],'CREDIT',transactionid,transactionrealted,transactiondetails)
				print(request.session['recivername'])
				transfer_into_another_account(request.user, request.user.username,
					request.session['recivername'], request.session['amount'],transactionid,transactionrealted,transactiondetails)
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









@csrf_exempt
def creditedmoney_user_wallet(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if not WithdrawMoneyWallet.objects.filter(vendor=vendor).exists():
			WithdrawMoneyWallet.objects.create(vendor=vendor)
		withdrawmoneywallet=WithdrawMoneyWallet.objects.filter(vendor=vendor).first()
		dic = {"vendorobj":vendor,'withdrawmoneywallet':withdrawmoneywallet,"storeobj":storeobj,
             "withdrawmoneywallettransaction":WithdrawMoneyWalletTransaction.objects.filter(withdrawmoneywallet__vendor=vendor)
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/creditedmoney_wallet-dash.html', dic)
	else:
		return render(request, '403.html')

@csrf_exempt
def account_type_details(request):
    response_data = {}
    account_type_group_data = []
    account_type_groups = AccountTypeGroup.objects.all()
    for account_type_group in account_type_groups:
        account_types = list(AccountType.objects.filter(accounttypegroup=account_type_group).values())
        account_type_group_data.append({
            'id': account_type_group.id,
            'name': account_type_group.name,
            'account_types': account_types
        })
    
    response_data['data'] = account_type_group_data
    return JsonResponse(response_data)



def account_code_by_store(store):
	storeobj=Store.objects.filter(id=store.id).first()
	if len(Account.objects.all()) != 0 :
		tds=Account.objects.filter().last()
		transid=tds.id
	else:
		transid=1
	start=0000+transid
	ref_no = str(str(timezone.now()))
	ref_no = ref_no.upper()
	ref_no = ref_no[0:4]
	transactionid=f"{storeobj.id}{ref_no}{start}"
	return transactionid



@csrf_exempt
def chartofaccounts(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
        
        
		if not Account.objects.filter(store=storeobj,accountname='Cash').exists():
			accounttypelist =AccountTypeList.objects.filter(name="Cash In Hand").first()
			Account.objects.create(store=storeobj,
				accountname='Cash',accounttypelist=accounttypelist,
				accountcode = account_code_by_store(storeobj),
				openingbalance = 0,
				transctiontype  =  'DEBIT')
		if not Account.objects.filter(store=storeobj,accountname='Purchase Entery').exists():
			accounttypelist =AccountTypeList.objects.filter(name="Purchase Accounts").first()
			Account.objects.create(store=storeobj,
				accountname='Purchase Entery',accounttypelist=accounttypelist,
				accountcode = account_code_by_store(storeobj),
				openingbalance = 0,
				transctiontype  =  'DEBIT')
   
		if not Account.objects.filter(store=storeobj,accountname='Sales Entery').exists():
			accounttypelist =AccountTypeList.objects.filter(name="Sales Accounts").first()
			Account.objects.create(store=storeobj,
				accountname='Sales Entery',accounttypelist=accounttypelist,
				accountcode = account_code_by_store(storeobj),
				openingbalance = 0,
				transctiontype  =  'CREDIT')
   
		if not Account.objects.filter(store=storeobj,accountname='Inventory Stock').exists():
			accounttypelist =AccountTypeList.objects.filter(name="Stock In Hand").first()
			Account.objects.create(store=storeobj,
				accountname='Inventory Stock',accounttypelist=accounttypelist,
				accountcode = account_code_by_store(storeobj),
				openingbalance = 0,
				transctiontype  =  'CREDIT')

		if not Account.objects.filter(store=storeobj,accountname='Profit & Loss').exists():
			Account.objects.create(store=storeobj,
				accountname='Profit & Loss',
				accountcode = account_code_by_store(storeobj),
				openingbalance = 0,
				transctiontype  =  'CREDIT')
		try:
			Trading_Account_Profit_and_Loss(storeobj)
		except:
			pass
		dic = {"vendorobj":vendor,"storeobj":storeobj,
                "accountledgerlist" :Account.objects.filter(store=storeobj),
               "accounttypegroups" :AccountTypeGroup.objects.all(),
		
           	# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/chartofaccounts.html', dic)
	else:
		return render(request, '403.html')





@csrf_exempt
def  accountledgertransactionshistory(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()  
		if AccountTransaction.objects.filter(account__id=id).exists():
			accounttransaction=AccountTransaction.objects.filter(account__id=id) 
		else:
			accounttransaction=None
            
		dic = {"vendorobj":vendor,'storeobj':storeobj,
				"accountledger" :Account.objects.filter(id=id).first(),
				"accounttypegroups" :AccountTypeGroup.objects.all(),
				'accounttransaction':accounttransaction
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/accounttransactionshistory.html', dic)
	else:
		return render(request, '403.html')




@csrf_exempt
def addchartofaccounts(request):
	if check_user_authentication(request, 'VENDOR'):    
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()  
		if request.method == 'POST':
		
			accountypelist = request.POST.get('accountypelist')
			accountname = request.POST.get('accountname')
			openingbalance = request.POST.get('openingbalance')
			transctiontype = request.POST.get('transctiontype')
			print(accountname,'accountname')
     
			if not Account.objects.filter(accountname=accountname,store = storeobj).exists():
				accountobj=Account()
				accountobj.store = storeobj
				accountobj.accounttypelist =AccountTypeList.objects.filter(id=accountypelist).first()
				accountobj.accountname = accountname
				accountobj.accountcode = account_code_by_store(storeobj)
				accountobj.openingbalance = openingbalance
				accountobj.transctiontype=transctiontype
				accountobj.updatedby= request.user
				accountobj.save()
				messages.info(request, 'Account Ledger is created successfully !')
				return redirect("/vendor/chart-of-account")
			else:
				messages.warning(request, 'Account Ledger is Already Exists')
				return redirect("/vendor/chart-of-account")
	else:
		return render(request, '403.html')





@csrf_exempt
def editchartofaccounts(request,id):
	if check_user_authentication(request, 'VENDOR'):  
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()  
		if request.method == 'POST':
			
			accountypelist = request.POST.get('accountypelist')
			accountname = request.POST.get('accountname')
			openingbalance = request.POST.get('openingbalance')
			transctiontype = request.POST.get('transctiontype')
			streetaddress =  request.POST.get('streetaddress')
			nearbyaddress =  request.POST.get('nearbyaddress')
			pincode = request.POST.get('pincode')
			city= request.POST.get('city')
			state= request.POST.get('state')
			country= request.POST.get('country')
			latitude =  request.POST.get('latitude')
			longitude =  request.POST.get('longitude')
			pancardno=request.POST.get('pancardno')
			pancarddoc = request.FILES.get('pancarddoc')
			gstno=request.POST.get('gstno')
			gstnodoc = request.FILES.get('gstnodoc')

			print(accountname,'accountname')
     
			if Account.objects.filter(id=id).exists():
				accountobj=Account.objects.filter(id=id).first()
				accountobj.store = storeobj
				if accountypelist:
					accountobj.accounttypelist =AccountTypeList.objects.filter(id=accountypelist).first()
				if accountname:
					accountobj.accountname = accountname
				
				accountobj.updatedby= request.user
				if streetaddress:
					accountobj.streetaddress =  streetaddress
				if nearbyaddress:
					accountobj.nearbyaddress =  nearbyaddress
				if pincode:
					accountobj.pincode = pincode
				if city:
					accountobj.city= city
				if state:
					accountobj.state= state
				if country:
					accountobj.country= country

				if pancardno:
					accountobj.pancardno=pancardno
				if pancarddoc:
					accountobj.pancarddoc =pancarddoc
				if gstno:
					accountobj.gstno=gstno
				if gstnodoc:
					accountobj.gstnodoc =gstnodoc
				accountobj.save()
				messages.info(request, 'Account Ledger is updated successfully !')
				return redirect("/vendor/chart-of-account")
			else:
				messages.warning(request, 'Account Ledger is not Exists')
				return redirect("/vendor/chart-of-account")
	else:
		return render(request, '403.html')



@csrf_exempt
def manualjournal(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
                "accountledgerlist" :Account.objects.filter(store=storeobj).exclude(accountname__in=["Profit & Loss", "Purchase Entery", "Sales Entery"]
),
               "accounttypegroups" :AccountTypeGroup.objects.all(),
                  "manualjournalvoucher" :ManualJournalVoucher.objects.filter(store=storeobj),
               
           	# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/manualjournal.html', dic)
	else:
		return render(request, '403.html')


from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import uuid

@csrf_exempt
def add_manualjournal(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == "POST":
			
			value = request.POST.get('hidden')
			description = request.POST.get('description')
			date = request.POST.get('journal_date')

			ref_no = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(timezone.now()) + 'JOURNAL'))
			ref_no = ref_no.upper()
			referenceno = ref_no[0:8]

			manualjournalvoucher = ManualJournalVoucher.objects.create(
				store=storeobj, referenceno=referenceno, createddate=date, description=description
			)

			total_amount = 0.0
			total_debit = 0.0
			total_credit = 0.0

			for i in range(int(value)):
				t = 'transaction' + str(i)
				a = 'account' + str(i)
				deb = 'deb' + str(i)
				cre = 'cre' + str(i)
				account_name = request.POST.get(a)
				transactiontype = request.POST.get(t)
				debit = request.POST.get(deb)
				credit = request.POST.get(cre)

				try:
					if account_name.isnumeric():
						account = Account.objects.get(id=account_name)
					else:
						account = Account.objects.filter(accountname=account_name).first()
					
					if not account:
						continue  # Skip this iteration if account is not found

					if debit:
						debit=float(debit)
						total_debit += float(debit)
						total_amount += float(debit)
						AccountEntry.objects.create(
							manualjournalvoucher=manualjournalvoucher, transactiontype=transactiontype,
							totaldebit=float(debit), account=account,updatedby=request.user,
						)
      
      
						if account.transctiontype=="DEBIT":
							currentopeningbalance=account.openingbalance
							if description:
								transactiondetails=description
							else:
								transactiondetails=f'Amount has been debit Rs.{debit}/-'
							accounttransactions = AccountTransaction.objects.create(
								account = account,previousprtransactiontype="DEBIT",
								transactiondate = timezone.now(),
								transactiontype = 'DEBIT', transactionrealted= "MANUAL-JOURNAL",
								transactiondetails = transactiondetails,
								transactionid = referenceno,
								transactionamount = debit,
								previousamount = round(account.openingbalance, 2),
								remainingamount =round(( round(account.openingbalance,2) + round(debit,2)),2)
							)
							account.openingbalance = round((currentopeningbalance + float(debit)),2)
							account.save()
						else:
							currentopeningbalance=account.openingbalance
							if currentopeningbalance < debit :
								if description:
									transactiondetails=description
								else:
									transactiondetails=f'Amount has been debit Rs.{debit}/-'
								accounttransactions = AccountTransaction.objects.create(
									account = account,
									transactiondate = timezone.now(),
									transactiontype = 'DEBIT', transactionrealted= "MANUAL-JOURNAL",
									transactiondetails = transactiondetails,
									transactionid = referenceno,previousprtransactiontype="DEBIT",
									transactionamount = debit,
									previousamount = round(account.openingbalance, 2),
									remainingamount = round(( round(debit,2)- round(account.openingbalance,2)),2)
								)
								account.openingbalance = round((float(debit - currentopeningbalance)),2)
								account.transctiontype="DEBIT"
								account.save()
								
							else:
								if description:
									transactiondetails=description
								else:
									transactiondetails=f'Amount has been debit Rs.{debit}/-'
								accounttransactions = AccountTransaction.objects.create(
									account = account,
									transactiondate = timezone.now(),
									transactiontype = 'DEBIT', transactionrealted= "MANUAL-JOURNAL",
									transactiondetails = transactiondetails,previousprtransactiontype="CREDIT",
									transactionid = referenceno,
									transactionamount = debit,
									previousamount = round(account.openingbalance, 2),
									remainingamount = round(( round(account.openingbalance,2) - round(debit,2)),2)
								)
								account.openingbalance = round((currentopeningbalance - float(debit)),2)
								account.save()
								
					if credit:
						credit=float(credit)

						total_credit += float(credit)
						AccountEntry.objects.create(
							manualjournalvoucher=manualjournalvoucher, transactiontype=transactiontype,
							totalcredit=float(credit), account=account,updatedby=request.user
						)
						if account.transctiontype=="DEBIT":
							currentopeningbalance=account.openingbalance
							if currentopeningbalance < credit :
								if description:
									transactiondetails=description
								else:
									transactiondetails=f'Amount has been credit Rs.{credit}/-'
								accounttransactions = AccountTransaction.objects.create(
									account = account,
									transactiondate = timezone.now(),
									transactiontype = 'CREDIT', transactionrealted= "MANUAL-JOURNAL",
									transactiondetails = transactiondetails,previousprtransactiontype="CREDIT",
									transactionid = referenceno,
									transactionamount = credit,
									previousamount = round(account.openingbalance, 2),
									remainingamount = round((round(credit,2) - round(account.openingbalance,2)),2)
								)						
        
								account.openingbalance = round((float(credit - currentopeningbalance)),2)
								account.transctiontype="CREDIT"
								account.save()
							
							else:
								if description:
									transactiondetails=description
								else:
									transactiondetails=f'Amount has been credit Rs.{credit}/-'
								accounttransactions = AccountTransaction.objects.create(
									account = account,
									transactiondate = timezone.now(),
									transactiontype = 'CREDIT', transactionrealted= "MANUAL-JOURNAL",
									transactiondetails = transactiondetails,previousprtransactiontype="DEBIT",
									transactionid = referenceno,
									transactionamount = credit,
									previousamount = round(account.openingbalance, 2),
									remainingamount = round(( round(account.openingbalance,2)- round(credit,2)),2)
								)	
								account.openingbalance = round((currentopeningbalance - float(credit)),2)
								account.save()
								
						else:
							currentopeningbalance=account.openingbalance
							if description:
								transactiondetails=description
							else:
								transactiondetails=f'Amount has been credit Rs.{credit}/-'
							accounttransactions = AccountTransaction.objects.create(
								account = account,
								transactiondate = timezone.now(),
								transactiontype = 'CREDIT', transactionrealted= "MANUAL-JOURNAL",
								transactiondetails = transactiondetails,previousprtransactiontype="CREDIT",
								transactionid = referenceno,
								transactionamount = credit,
								previousamount = round(account.openingbalance, 2),
								remainingamount =  round((round(account.openingbalance,2) + round(credit,2)),2)
							)
							account.openingbalance = round((currentopeningbalance + float(credit)),2)
							account.save()
							

				except Account.DoesNotExist:
					continue  # Skip this iteration if account does not exist

			manualjournalvoucher.totalcredit = total_credit
			manualjournalvoucher.totaldebit = total_debit
			manualjournalvoucher.amount = total_amount
			manualjournalvoucher.updatedby=request.user
			manualjournalvoucher.save()

		return redirect("/vendor/manual-journal")
	else:
		return render(request, '403.html')




@csrf_exempt
def view_manualjournal(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
				"accountledgerlist" :Account.objects.filter(store=storeobj).exclude(accountname="Profit & Loss"),
				"accounttypegroups" :AccountTypeGroup.objects.all(),
					"manualjournalvoucher" :ManualJournalVoucher.objects.filter(store=storeobj,id=id),
				
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/manualjournalupdated.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def Purchase_Vouchers(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
                "sellerledgerlist" :Account.objects.filter(store=storeobj,accounttypelist__name="Seller"),
                "purchaseledger" :Account.objects.filter(store=storeobj,accountname="Purchase Entery").first(),
               "accounttypegroups" :AccountTypeGroup.objects.all(),
               'itemlist': ProductVariants.objects.filter(store=storeobj),
                'purchasesorder': PurchasesOrder.objects.filter(store=storeobj, type = "PURCHASE-VOUCHER"),
		
           	# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/purchasevoucher.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def Purchase_Vouchers_Details(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
                "sellerledgerlist" :Account.objects.filter(store=storeobj,accounttypelist__name="Seller"),
                "purchaseledger" :Account.objects.filter(store=storeobj,accountname="Purchase Entery").first(),
               "accounttypegroups" :AccountTypeGroup.objects.all(),
               'itemlist': ProductVariants.objects.filter(store=storeobj),
                'purchasesorder': PurchasesOrder.objects.filter(store=storeobj, type = "PURCHASE-VOUCHER",id=id).first(),
		
           	# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/purchasevoucherdetails.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def Add_Purchase_Vouchers(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		if request.method == "POST":
			
			value = request.POST.get('hidden')
			purchase_date = request.POST.get('purchase_date')
			supplierinvoiceno = request.POST.get('supplierinvoiceno')
			sellerledgeraccount = request.POST.get('sellerledgeraccount')
			purchaseledgeraccount = request.POST.get('purchaseledgeraccount')
			description = request.POST.get('description')
			totaltax = request.POST.get('totaltax')
			totaltax=float(totaltax)
			totalamount = request.POST.get('totalamount')
			totalamount=float(totalamount)

            
   
			selleraccount=Account.objects.filter(store=storeobj,accounttypelist__name="Seller",id=sellerledgeraccount).first()
			purchaseledger=Account.objects.filter(store=storeobj,accountname="Purchase Entery").first()
			inventorystockledger=Account.objects.filter(store=storeobj,accountname='Inventory Stock').first()
			ref_no = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(timezone.now()) + 'JOURNAL'))
			ref_no = ref_no.upper()
			referenceno = ref_no[0:8]

			purchasevoucher = PurchasesOrder.objects.create(
                type = "PURCHASE-VOUCHER",
				store=storeobj, orderno=referenceno, createdat=purchase_date, supplierinvoiceno=supplierinvoiceno,selleraccount=selleraccount
			)

			

			for i in range(int(value)):
				itemproduct = 'itemproduct' + str(i)
				price = 'price' + str(i)
				quantity = 'quantity' + str(i)
				tax = 'tax' + str(i)
				total = 'total' + str(i)
				productvariantid = request.POST.get(itemproduct)
				productprice = request.POST.get(price)
				productquantity = request.POST.get(quantity)
				producttax = request.POST.get(tax)
				producttotal = request.POST.get(total)
                
				print(productprice,productquantity,producttotal,'price')

				try:
					if productvariantid.isnumeric():
						productvariants = ProductVariants.objects.get(id=productvariantid)
					else:
						productvariants = ProductVariants.objects.filter(productvariantname=productvariantid).first()
					
					if not productvariants:
						continue  # Skip this iteration if account is not found

					if productvariants:
						PurchasesOrderItems.objects.create(store=storeobj,
							purchasesorder=purchasevoucher, productvariants=productvariants,price=float(productprice),
							tax=float(producttax),total=float(producttotal), quantity=int(productquantity),updatedby=request.user,
						)
						ptotal=float(producttotal)
						quantity=int(productquantity)
						inventorystockledgercurrentopeningbalance=inventorystockledger.openingbalance
						if inventorystockledger.transctiontype=="CREDIT":	
							accounttransactions = AccountTransaction.objects.create(
								account = inventorystockledger,previousprtransactiontype="CREDIT",
								transactiondate = timezone.now(),
								transactiontype = 'CREDIT', transactionrealted= "PURCHASE-VOUCHER",
								transactiondetails = f'Amount {ptotal} has been credit for item purchase : {productvariants.productvariantname} with {quantity} quantity.',
								transactionid = referenceno,
								transactionamount = ptotal,
								previousamount = round(inventorystockledger.openingbalance, 2),
								remainingamount =round((inventorystockledger.openingbalance + ptotal),2)
							)
							inventorystockledger.openingbalance = round((inventorystockledgercurrentopeningbalance + float(ptotal)),2)
							inventorystockledger.save()
						else:
							if inventorystockledgercurrentopeningbalance < ptotal :
								accounttransactions = AccountTransaction.objects.create(
									account = inventorystockledger,previousprtransactiontype="DEBIT",
									transactiondate = timezone.now(),
									transactiontype = 'CREDIT', transactionrealted= "PURCHASE-VOUCHER",
									transactiondetails = f'Amount {ptotal} has been credit for item purchase : {productvariants.productvariantname} with {quantity} quantity.',
									transactionid = referenceno,
									transactionamount = ptotal,
									previousamount = round(inventorystockledger.openingbalance, 2),
									remainingamount =round(( ptotal - inventorystockledger.openingbalance),2)
								)
								inventorystockledger.openingbalance = round((float(ptotal)- inventorystockledgercurrentopeningbalance),2)
								inventorystockledger.transctiontype="DEBIT"
								inventorystockledger.save()
							else:
								accounttransactions = AccountTransaction.objects.create(
										account = inventorystockledger,previousprtransactiontype="DEBIt",
										transactiondate = timezone.now(),
										transactiontype = 'CREDIT', transactionrealted= "PURCHASE-VOUCHER",
										transactiondetails = f'Amount {ptotal} has been credit for item purchase : {productvariants.productvariantname} with {quantity} quantity.',
										transactionid = referenceno,
										transactionamount = ptotal,
										previousamount = round(inventorystockledger.openingbalance, 2),
										remainingamount =round((inventorystockledger.openingbalance - ptotal),2)
									)
								inventorystockledger.openingbalance = round((inventorystockledgercurrentopeningbalance - float(ptotal)),2)
								inventorystockledger.save()
									
						openingbalance=inventorystockledger.openingbalance
						curentquantity=productvariants.quantity
						totalquantity=curentquantity + int(productquantity)
						averageprice=round((openingbalance / totalquantity),2)
						productvariants.purchaseprice=averageprice
						productvariants.quantity=totalquantity
						productvariants.save()
						
     						
				except ProductVariants.DoesNotExist:
					continue  # Skip this iteration if account does not exist
            
			selleraccountcurrentopeningbalance=selleraccount.openingbalance
			purchaseledgercurrentopeningbalance=purchaseledger.openingbalance
   
			if purchaseledger.transctiontype=="DEBIT":
				accounttransactions = AccountTransaction.objects.create(
					account = purchaseledger,previousprtransactiontype="DEBIT",
					transactiondate = timezone.now(),
					transactiontype = 'DEBIT', transactionrealted= "PURCHASE-VOUCHER",
					transactiondetails = f'Amount {totalamount} has been debit for item purchase',
					transactionid = referenceno,
					transactionamount = totalamount,
					previousamount = round(purchaseledger.openingbalance, 2),
					remainingamount = round((purchaseledger.openingbalance + totalamount),2)
				)
				purchaseledger.openingbalance = round((purchaseledgercurrentopeningbalance + float(totalamount)),2)
				purchaseledger.save()
			else:
				if purchaseledgercurrentopeningbalance < totalamount :	
					accounttransactions = AccountTransaction.objects.create(
						account = purchaseledger,previousprtransactiontype="CREDIT",
						transactiondate = timezone.now(),
						transactiontype = 'DEBIT', transactionrealted= "PURCHASE-VOUCHER",
						transactiondetails = f'Amount {totalamount} has been debit for item purchase',
						transactionid = referenceno,
						transactionamount = totalamount,
						previousamount = round(purchaseledger.openingbalance, 2),
						remainingamount = round((totalamount - purchaseledger.openingbalance),2)
					)
					purchaseledger.openingbalance = round((float(totalamount) - purchaseledgercurrentopeningbalance ),2)
					purchaseledger.transctiontype="DEBIT"
					purchaseledger.save()
				else:
					accounttransactions = AccountTransaction.objects.create(
						account = purchaseledger,previousprtransactiontype="CREDIT",
						transactiondate = timezone.now(),
						transactiontype = 'DEBIT', transactionrealted= "PURCHASE-VOUCHER",
						transactiondetails = f'Amount {totalamount} has been debit for item purchase',
						transactionid = referenceno,
						transactionamount = totalamount,
						previousamount = round(purchaseledger.openingbalance, 2),
						remainingamount = round((purchaseledger.openingbalance - totalamount),2)
					)
					purchaseledger.openingbalance = round((purchaseledgercurrentopeningbalance - float(totalamount)),2)
					purchaseledger.save()
				
			if selleraccount.transctiontype=="CREDIT":	
				accounttransactions = AccountTransaction.objects.create(
					account = selleraccount,previousprtransactiontype="CREDIT",
					transactiondate = timezone.now(),
					transactiontype = 'CREDIT', transactionrealted= "PURCHASE-VOUCHER",
					transactiondetails = f'Amount {totalamount} has been credit for item purchase',
					transactionid = referenceno,
					transactionamount = totalamount,
					previousamount = round(selleraccount.openingbalance, 2),
					remainingamount =round((selleraccount.openingbalance + totalamount),2)
				)
				selleraccount.openingbalance = round((selleraccountcurrentopeningbalance + float(totalamount)),2)
				selleraccount.save()
			else:
				if selleraccountcurrentopeningbalance < totalamount :
					accounttransactions = AccountTransaction.objects.create(
						account = selleraccount,previousprtransactiontype="DEBIT",
						transactiondate = timezone.now(),
						transactiontype = 'CREDIT', transactionrealted= "PURCHASE-VOUCHER",
						transactiondetails = f'Amount {totalamount} has been credit for item purchase',
						transactionid = referenceno,
						transactionamount = totalamount,
						previousamount = round(selleraccount.openingbalance, 2),
						remainingamount =round(( totalamount - selleraccount.openingbalance),2)
					)
					selleraccount.openingbalance = round((float(totalamount) - selleraccountcurrentopeningbalance),2)
					selleraccount.transctiontype="DEBIT"
					selleraccount.save()
				else:
					accounttransactions = AccountTransaction.objects.create(
							account = selleraccount,previousprtransactiontype="DEBIT",
							transactiondate = timezone.now(),
							transactiontype = 'CREDIT', transactionrealted= "PURCHASE-VOUCHER",
							transactiondetails = f'Amount {totalamount} has been credit for item purchase',
							transactionid = referenceno,
							transactionamount = totalamount,
							previousamount = round(selleraccount.openingbalance, 2),
							remainingamount =round((selleraccount.openingbalance - totalamount),2)
						)
					selleraccount.openingbalance = round((selleraccountcurrentopeningbalance - float(totalamount)),2)
					selleraccount.save()
						
				
			purchasevoucher.description=description
			purchasevoucher.total = totalamount
			purchasevoucher.tax = totaltax
			purchasevoucher.subtotal = totalamount-totaltax
			purchasevoucher.updatedby=request.user
			purchasevoucher.save()

		return redirect("/vendor/purchase-vouchers")
	else:
		return render(request, '403.html')





@csrf_exempt
def Sales_Vouchers(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
                "buyerledgerlist" :Account.objects.filter(store=storeobj,accounttypelist__name="Buyer"),
                "salesledger" :Account.objects.filter(store=storeobj,accountname="Sales Entery").first(),
               "accounttypegroups" :AccountTypeGroup.objects.all(),
               'itemlist': ProductVariants.objects.filter(store=storeobj),
               'salessorder': SalesOrder.objects.filter(store=storeobj, type = "SALES-VOUCHER"),
		
           	# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/salesvoucher.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def Sales_Vouchers_Details(request,id):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,
                "buyerledgerlist" :Account.objects.filter(store=storeobj,accounttypelist__name="Buyer"),
                "salesledger" :Account.objects.filter(store=storeobj,accountname="Sales Entery").first(),
               "accounttypegroups" :AccountTypeGroup.objects.all(),
               'itemlist': ProductVariants.objects.filter(store=storeobj),
            	'salesorder': SalesOrder.objects.filter(store=storeobj, type = "SALES-VOUCHER",id=id).first(),
		
           	# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/accountant_app/salesvoucherdetails.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def Add_Sales_Vouchers(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
  
		if request.method == "POST":
			
			value = request.POST.get('hidden')
			sales_date = request.POST.get('sales_date')
			invoiceno = request.POST.get('invoiceno')
			buyerledgeraccount = request.POST.get('buyerledgeraccount')
			salesledgeraccount = request.POST.get('salesledgeraccount')
			description = request.POST.get('description')
			totaltax = request.POST.get('totaltax')
			totaltax=float(totaltax)
			totalamount = request.POST.get('totalamount')
			totalamount=float(totalamount)

            
			inventorystockledger=Account.objects.filter(store=storeobj,accountname='Inventory Stock').first()
			buyeraccount=Account.objects.filter(store=storeobj,accounttypelist__name="Buyer",id=buyerledgeraccount).first()
			salesledger=Account.objects.filter(store=storeobj,accountname="Sales Entery").first()
			ref_no = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(timezone.now()) + 'JOURNAL'))
			ref_no = ref_no.upper()
			referenceno = ref_no[0:8]

			purchasevoucher = SalesOrder.objects.create(
                type = "SALES-VOUCHER",
				store=storeobj, orderno=referenceno, createdat=sales_date,buyeraccount=buyeraccount
			)

			

			for i in range(int(value)):
				itemproduct = 'itemproduct' + str(i)
				price = 'price' + str(i)
				quantity = 'quantity' + str(i)
				tax = 'tax' + str(i)
				total = 'total' + str(i)
				productvariantid = request.POST.get(itemproduct)
				productprice = request.POST.get(price)
				productquantity = request.POST.get(quantity)
				producttax = request.POST.get(tax)
				producttotal = request.POST.get(total)
                
				print(productprice,productquantity,producttotal,'price')

				try:
					if productvariantid.isnumeric():
						productvariants = ProductVariants.objects.get(id=productvariantid)
					else:
						productvariants = ProductVariants.objects.filter(productvariantname=productvariantid).first()
					
					if not productvariants:
						continue  # Skip this iteration if account is not found

					if productvariants:
						SalesOrderItems.objects.create(store=storeobj,
							salesorder=purchasevoucher, productvariants=productvariants,vendorprice=float(productprice),
							vendortax=float(producttax),vendortotal=float(producttotal), quantity=int(productquantity),updatedby=request.user,
						)
      
						
						quantity=int(productquantity)
						curentquantity=productvariants.quantity
						totalquantity=curentquantity - int(productquantity)
						productvariants.quantity=totalquantity
						productvariants.save()
						ptotal=round((float(productvariants.purchaseprice) * quantity),2)
		
						inventorystockledgercurrentopeningbalance=inventorystockledger.openingbalance
						if inventorystockledger.transctiontype=="DEBIT":	
							accounttransactions = AccountTransaction.objects.create(
								account = inventorystockledger,previousprtransactiontype="DEBIT",
								transactiondate = timezone.now(),
								transactiontype = 'DEBIT', transactionrealted= "PURCHASE-SALES",
								transactiondetails = f'Amount {ptotal} has been debit for item sale : {productvariants.productvariantname} with {quantity} quantity.',
								transactionid = referenceno,
								transactionamount = ptotal,
								previousamount = round(inventorystockledger.openingbalance, 2),
								remainingamount =round((inventorystockledger.openingbalance + ptotal),2)
							)
							inventorystockledger.openingbalance = round((inventorystockledgercurrentopeningbalance + float(ptotal)),2)
							inventorystockledger.save()
						else:
							if inventorystockledgercurrentopeningbalance < ptotal :
								accounttransactions = AccountTransaction.objects.create(
									account = inventorystockledger,previousprtransactiontype="CREDIT",
									transactiondate = timezone.now(),
									transactiontype = 'DEBIT', transactionrealted= "PURCHASE-SALES",
									transactiondetails = f'Amount {ptotal} has been debit for item sale : {productvariants.productvariantname} with {quantity} quantity.',
									transactionid = referenceno,
									transactionamount = ptotal,
									previousamount = round(inventorystockledger.openingbalance, 2),
									remainingamount =round(( ptotal - inventorystockledger.openingbalance),2)
								)
								inventorystockledger.openingbalance = round((float(ptotal) - inventorystockledgercurrentopeningbalance),2)
								inventorystockledger.transctiontype="DEBIT"
								inventorystockledger.save()
							else:
								accounttransactions = AccountTransaction.objects.create(
										account = inventorystockledger,previousprtransactiontype="CREDIT",
										transactiondate = timezone.now(),
										transactiontype = 'DEBIT', transactionrealted= "SALES-VOUCHER",
										transactiondetails = f'Amount {ptotal} has been debit for item sale : {productvariants.productvariantname} with {quantity} quantity.',
										transactionid = referenceno,
										transactionamount = ptotal,
										previousamount = round(inventorystockledger.openingbalance, 2),
										remainingamount =round((inventorystockledger.openingbalance - ptotal),2)
									)
								inventorystockledger.openingbalance = round((inventorystockledgercurrentopeningbalance - float(ptotal)),2)
								inventorystockledger.save()
									
						
							
				except ProductVariants.DoesNotExist:
					continue  # Skip this iteration if account does not exist
            
			buyeraccountcurrentopeningbalance=buyeraccount.openingbalance
			salesledgercurrentopeningbalance=salesledger.openingbalance
          
			if salesledger.transctiontype=="CREDIT":	
		
				accounttransactions = AccountTransaction.objects.create(
					account = salesledger,previousprtransactiontype="CREDIT",
					transactiondate = timezone.now(),
					transactiontype = 'CREDIT', transactionrealted= "SALES-VOUCHER",
					transactiondetails = f'Amount {totalamount} has been credit for item sales',
					transactionid = referenceno,
					transactionamount = totalamount,
					previousamount = round(salesledger.openingbalance, 2),
					remainingamount = round((salesledger.openingbalance + totalamount),2)
				)
				salesledger.openingbalance = round((salesledgercurrentopeningbalance + float(totalamount)),2)
				salesledger.save()	
			else:
				if salesledgercurrentopeningbalance < totalamount :
					accounttransactions = AccountTransaction.objects.create(
					account = salesledger,previousprtransactiontype="DEBIT",
					transactiondate = timezone.now(),
					transactiontype = 'CREDIT', transactionrealted= "SALES-VOUCHER",
					transactiondetails = f'Amount {totalamount} has been credit for item sales',
					transactionid = referenceno,
					transactionamount = totalamount,
					previousamount = round(salesledger.openingbalance, 2),
					remainingamount = round((totalamount - salesledger.openingbalance),2)
					)
					salesledger.openingbalance = round(( float(totalamount) - salesledgercurrentopeningbalance ),2)
					salesledger.transctiontype="DEBIT"				
					salesledger.save()	
				else:
					accounttransactions = AccountTransaction.objects.create(
							account = salesledger,previousprtransactiontype="DEBIT",
							transactiondate = timezone.now(),
							transactiontype = 'CREDIT', transactionrealted= "SALES-VOUCHER",
							transactiondetails = f'Amount {totalamount} has been credit for item sales',
							transactionid = referenceno,
							transactionamount = totalamount,
							previousamount = round(salesledger.openingbalance, 2),
							remainingamount = round((salesledger.openingbalance - totalamount),2)
						)
					salesledger.openingbalance = round((salesledgercurrentopeningbalance - float(totalamount)),2)
					salesledger.save()
					
			if buyeraccount.transctiontype=="DEBIT":	
				accounttransactions = AccountTransaction.objects.create(
				account = buyeraccount,previousprtransactiontype="DEBIT",
				transactiondate = timezone.now(),
				transactiontype = 'DEBIT', transactionrealted= "SALES-VOUCHER",
				transactiondetails = f'Amount {totalamount} has been debit for item sales',
				transactionid = referenceno,
				transactionamount = totalamount,
				previousamount = round(buyeraccount.openingbalance, 2),
				remainingamount =round((buyeraccount.openingbalance + totalamount),2)
				)
				buyeraccount.openingbalance = round((buyeraccountcurrentopeningbalance + float(totalamount)),2)
				buyeraccount.save()
			else:
				if buyeraccountcurrentopeningbalance < totalamount :
					accounttransactions = AccountTransaction.objects.create(
					account = buyeraccount,previousprtransactiontype="CREDIT",
					transactiondate = timezone.now(),
					transactiontype = 'DEBIT', transactionrealted= "SALES-VOUCHER",
					transactiondetails = f'Amount {totalamount} has been debit for item sales',
					transactionid = referenceno,
					transactionamount = totalamount,
					previousamount = round(buyeraccount.openingbalance, 2),
					remainingamount =round((totalamount - buyeraccount.openingbalance ),2)
					)
					buyeraccount.openingbalance = round((float(totalamount- buyeraccountcurrentopeningbalance )),2)
					buyeraccount.transctiontype="DEBIT"			
					buyeraccount.save()
				else:
					accounttransactions = AccountTransaction.objects.create(
					account = buyeraccount,previousprtransactiontype="CREDIT",
					transactiondate = timezone.now(),
					transactiontype = 'DEBIT', transactionrealted= "SALES-VOUCHER",
					transactiondetails = f'Amount {totalamount} has been debit for item sales',
					transactionid = referenceno,
					transactionamount = totalamount,
					previousamount = round(buyeraccount.openingbalance, 2),
					remainingamount =round((buyeraccount.openingbalance - totalamount),2)
					)
					buyeraccount.openingbalance = round((buyeraccountcurrentopeningbalance - float(totalamount)),2)
					buyeraccount.save()	
			
					
			purchasevoucher.description=description
			purchasevoucher.invoiceno=invoiceno
			purchasevoucher.vendortotal = totalamount
			purchasevoucher.vendortax = totaltax
			purchasevoucher.vendorsubtotal = totalamount-totaltax
			purchasevoucher.updatedby=request.user
			purchasevoucher.save()

		return redirect("/vendor/sales-vouchers")
	else:
		return render(request, '403.html')





from django.http import JsonResponse

def fetch_productvaraints_related_data(request):
	itemproductid = request.GET.get('itemproductid', '')
	quantity = request.GET.get('quantity', '')
	price = request.GET.get('price', '')
	print(itemproductid,quantity,price,'itemproductid')

	try:
		item = ProductVariants.objects.get(id=itemproductid)
		quantity=float(quantity)
		if price :
			vendorprice = float(price)
		else:
			vendorprice = item.purchaseprice
		taxrate=item.product.tax
  
        
		vendorperproducttax= round( (vendorprice) * ((item.product.tax/100) / (1 + (item.product.tax/100))),2)
		lpurchaseprice=round((vendorprice - vendorperproducttax),2)

		vendortax = round((vendorperproducttax * quantity),2)
		subtotal=round((lpurchaseprice * quantity),2)	
		vendortotal=round((vendorprice * quantity),2)
		productvariantname=item.productvariantname
		
		purchaseprice=vendorprice
		print(purchaseprice,item.purchaseprice,vendorperproducttax,'vendorperproducttax')
		
		data = {'productvariantname': productvariantname,'taxrate':taxrate,'subtotal':subtotal ,"purchaseprice":purchaseprice,
					'tax': vendortax, 'total': vendortotal,
     
     }
	except ProductVariants.DoesNotExist:
		data = {'productvariantname': '', 'purchaseprice': ''}

	return JsonResponse(data)



def fetch_productvaraints_sales_related_data(request):
	itemproductid = request.GET.get('itemproductid', '')
	quantity = request.GET.get('quantity', '')
	price = request.GET.get('price', '')
	print(itemproductid,quantity,price,'itemproductid')

	try:
		item = ProductVariants.objects.get(id=itemproductid)
		quantity=float(quantity)
		if price :
			vendorprice = float(price)
		else:
			vendorprice = item.price
   
		taxrate=item.product.tax
  
		vendorperproducttax= round( (vendorprice) * ((item.product.tax/100) / (1 + (item.product.tax/100))),2)
		lpurchaseprice=round((vendorprice - vendorperproducttax),2)

		vendortax = round((vendorperproducttax * quantity),2)
		subtotal=round((lpurchaseprice * quantity),2)	
		vendortotal=round((vendorprice * quantity),2)
		

		productvariantname=item.productvariantname
		
		salesprice=vendorprice
		print(salesprice,item.purchaseprice,vendorperproducttax,'vendorperproducttax')
		
		data = {'productvariantname': productvariantname,'taxrate':taxrate, 'subtotal':subtotal,"salesprice":salesprice,
					'tax': vendortax, 'total': vendortotal,
     
     }
	except ProductVariants.DoesNotExist:
		data = {'productvariantname': '', 'salesprice': ''}

	return JsonResponse(data)



@csrf_exempt
def viewtrialBalance(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
                
				"accountledgerlist" :Account.objects.filter(store=storeobj),
				"accounttypegroups" :AccountTypeGroup.objects.all(),
					"manualjournalvoucher" :ManualJournalVoucher.objects.filter(store=storeobj),
				
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/report/trialbalance.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def viewtradingaccount(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,"storeobj":storeobj,
                
				"accountledgerlist" :Account.objects.filter(store=storeobj),
				"accounttypegroups" :AccountTypeGroup.objects.all(),
					"manualjournalvoucher" :ManualJournalVoucher.objects.filter(store=storeobj),
				
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/report/tradingaccount.html', dic)
	else:
		return render(request, '403.html')





@csrf_exempt
def viewbalancesheet(request):
	if check_user_authentication(request, 'VENDOR'):
		vendor = Vendor.objects.filter(user=request.user).first()
		storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()
		dic = {"vendorobj":vendor,'storeobj':storeobj,
				"accountledgerlist" :Account.objects.filter(store=storeobj),
				"accounttypegroups" :AccountTypeGroup.objects.all(),
				"manualjournalvoucher" :ManualJournalVoucher.objects.filter(store=storeobj),
				
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/report/balancesheet.html', dic)
	else:
		return render(request, '403.html')



def Trial_Balance(request):
	if not check_user_authentication(request, 'VENDOR'):
		return JsonResponse({'error': 'Unauthorized'}, status=401)

	vendor = Vendor.objects.filter(user=request.user).first()
	storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()

	trail_data = {}

	accounttypegroups = AccountTypeGroup.objects.all()

	for group in accounttypegroups:
		group_total_debit = 0
		group_total_credit = 0
		group_data = {"types": [], "total_debit": 0, "total_credit": 0}

		accounttypes = AccountType.objects.filter(accounttypegroup=group)

		for account_type in accounttypes:
			type_total_debit = 0
			type_total_credit = 0
			type_data = {"lists": [], "total_debit": 0, "total_credit": 0}

			accounttypelists = AccountTypeList.objects.filter(accounttype=account_type)

			for account_typelist in accounttypelists:
				list_total_debit = 0
				list_total_credit = 0
				list_data = {"accounts": [], "total_debit": 0, "total_credit": 0}

				accounts = Account.objects.filter(accounttypelist=account_typelist, store=storeobj)

				for account in accounts:
					balance = account.openingbalance  # Assume balance is stored here
					account_data = {
						"accountname": account.accountname,
						"accountcode": account.accountcode,
						"balance": balance,
						"transctiontype": account.transctiontype
					}
					if account.transctiontype == 'DEBIT':  # Debit balance
						list_total_debit += balance
					else:  # Credit balance
						list_total_credit += balance
					
					list_data["accounts"].append(account_data)

				list_data["total_debit"] = list_total_debit
				list_data["total_credit"] = list_total_credit

				type_total_debit += list_total_debit
				type_total_credit += list_total_credit
				type_data["lists"].append({"name": account_typelist.name, "data": list_data})

			type_data["total_debit"] = type_total_debit
			type_data["total_credit"] = type_total_credit

			group_total_debit += type_total_debit
			group_total_credit += type_total_credit
			group_data["types"].append({"name": account_type.name, "data": type_data})

		group_data["total_debit"] = group_total_debit
		group_data["total_credit"] = group_total_credit

		trail_data[group.name] = group_data

	return JsonResponse(trail_data)




def Trading_Account(request):
	if not check_user_authentication(request, 'VENDOR'):
		return JsonResponse({'error': 'Unauthorized'}, status=401)

	vendor = Vendor.objects.filter(user=request.user).first()
	storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()

	trading_data = {
		"Sales": {"credit": 0, "details": []},
        "Closing Inventory Stock": {"credit": 0, "details": []},
		"Purchases": {"debit": 0, "details": []},
		"Direct Expenses": {"debit": 0, "details": []},
		"Gross Profit": {"debit": 0},
		"Gross Loss": {"credit": 0},
	}

	accounts = Account.objects.filter(store=storeobj).exclude(accountname="Profit & Loss")

	for account in accounts:
		account_data = {
			"accountname": account.accountname,
			"accountcode": account.accountcode,
			"balance": account.openingbalance,
			"transctiontype": account.transctiontype,
		}

		if account.accounttypelist.accounttype.name == 'Sales':
			trading_data["Sales"]["credit"] += account.openingbalance
			trading_data["Sales"]["details"].append(account_data)
   
		elif account.accounttypelist.name == 'Stock In Hand':
			trading_data["Closing Inventory Stock"]["credit"] += account.openingbalance
			trading_data["Closing Inventory Stock"]["details"].append(account_data)

		elif account.accounttypelist.accounttype.name == 'Purchases':
			trading_data["Purchases"]["debit"] += account.openingbalance
			trading_data["Purchases"]["details"].append(account_data)

		elif account.accounttypelist.accounttype.name == 'Direct Expenses':
			trading_data["Direct Expenses"]["debit"] += account.openingbalance
			trading_data["Direct Expenses"]["details"].append(account_data)

	gross_profit = (trading_data["Sales"]["credit"] + trading_data["Closing Inventory Stock"]["credit"]) - (trading_data["Purchases"]["debit"] + trading_data["Direct Expenses"]["debit"])
	
	if gross_profit > 0:
		trading_data["Gross Profit"]["debit"] = gross_profit
	else:
		trading_data["Gross Loss"]["credit"] = -gross_profit

	return JsonResponse(trading_data)



def Balance_Sheet(request):
    if not check_user_authentication(request, 'VENDOR'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    vendor = Vendor.objects.filter(user=request.user).first()
    storeobj = Store.objects.filter(vendor=vendor,isselectedcurrentstore=True).first()

    
    balance_sheet_data = {
        "Assets": {"total": 0, "details": []},
        "Liabilities": {"total": 0, "details": []},
    }

    accounts = Account.objects.filter(store=storeobj).exclude(accountname="Profit & Loss")

    for account in accounts:
        account_data = {
            "accountname": account.accountname,
            "accountcode": account.accountcode,
            "balance": account.openingbalance,
            "transctiontype": account.transctiontype,
        }

        if account.accounttypelist.accounttype.accounttypegroup.name == 'Assets':
            balance_sheet_data["Assets"]["total"] += account.openingbalance
            balance_sheet_data["Assets"]["details"].append(account_data)
        elif account.accounttypelist.accounttype.accounttypegroup.name == 'Liabilities':
            balance_sheet_data["Liabilities"]["total"] += account.openingbalance
            balance_sheet_data["Liabilities"]["details"].append(account_data)

    return JsonResponse(balance_sheet_data)
