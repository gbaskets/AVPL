import os
from django.shortcuts import render
from django.conf import settings
import re
import qrcode
# Create your views here.
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators import csrf
from admin_app.models import *
from inventory_app.models import *
from main_app.models import *
from vendor_app.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import JsonResponse
import uuid
import datetime
from main_app.utils import *
from main_app.razor import *
from admin_app.utils import *
from django.utils import timezone
import base64
from django.core.files.base import ContentFile


@csrf_exempt
def admin_show(request):
#	for x in ProductCategory.objects.all():
#		PointValue.objects.create(category=x)
#	ProductCategory.objects.filter(name='Computers').delete()
#	User.objects.create_user(email='admin@avpl.com',username='adminavpl',password='1234')
#	user = User.objects.get(email='admin@avpl.com')
#	Role(user=user, level=Levels.objects.get(level='Admin')).save()
	return HttpResponse('Done!')

@csrf_exempt
def admin_login(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		if User.objects.filter(email=email).exists():
			chk_user = User.objects.get(email=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if check_user_authentication(request, 'ADMIN'):
					return redirect('/admins/dashboard')
				else:
					messages.info(request, 'You are not allowed to login')
					logout(request)
					return redirect('/admins/')
			else:
				messages.info(request,'Incorrect Admin Password')
				return redirect('/admins/')
		elif User.objects.filter(username=email).exists():
			chk_user = User.objects.get(username=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if check_user_authentication(request, 'ADMIN'):
					return redirect('/admins/dashboard')
				else:
					messages.info(request, 'You are not allowed to login')
					logout(request)
					return redirect('/admins/')
			else:
				messages.info(request,'Incorrect Admin Password')
				return redirect('/admins/')
		else:
			messages.info(request,'Incorrect Admin Email/Username')
			return redirect('/admins/')
	else:
		if request.user.is_authenticated and check_user_authentication(request, 'ADMIN'):
			return redirect('/admins/dashboard')
		else:
			return render(request, 'admin_app/login.html', {})
@csrf_exempt
def admin_dashboard(request):
	if check_user_authentication(request, 'ADMIN'):
		if len(CommissionWallet.objects.filter(admin=request.user)) == 0:
			CommissionWallet.objects.create(admin=request.user,isactive=True)
		if len(Wallet.objects.filter(admin=request.user)) == 0:
			Wallet.objects.create(admin=request.user,isactive=True)
		
		pv = 0.0
		# pv_year = 0.0
		d = datetime.datetime.now()
		# for pv_trn in PVTransactions.objects.all():
		# 	if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
		# 		pv += pv_trn.pv
			
		# # for pv_trn in PVTransactions.objects.all():
		# # 	if pv_trn.transaction_date.strftime("%Y") == d.strftime("%Y"):
		# # 		pv_year += pv_trn.pv
		# # Yearly_PV.objects.update(pv = pv_year)
		# # print(pv_year<pv)
		# pv = round(pv,2)
		dic = {
			'categories':ProductCategory.objects.all(),
			'commission':CommissionWallet.objects.filter(admin=request.user).first(),
			'wallet':Wallet.objects.filter(admin=request.user).first(),
			'commissiontransactions':CommissionWalletTransaction.objects.all().order_by('-id'),
			# 'total_pv':Current_PV.objects.all().order_by('-id').first,
			# 'year_pv':Yearly_PV.objects.all(),
			'wallettransactions':WalletTransaction.objects.all().order_by('-id'),
			# 'notification':get_notifications(request.user,'ADMIN'),
			# 'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/dashboard.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

from django.contrib.auth.decorators import login_required
from main_app.models import *
import random

from django.db import transaction

@csrf_exempt
def admin_send_money(request):
	if check_user_authentication(request, 'ADMIN'):

		user=WalletTransferApprovalSettings.objects.all()[0:1]
		print(user)

		if WalletTransferApprovalSettings.objects.get(id =user).admin == 1:
			
			request.session['senderotp'] = random.randint(100000,999999)
			request.session['timer'] = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
			print(request.session['timer'])

			print(request.session['senderotp'],'\n---------->','HHHHHHHHHHHHHH')
			msg = ''' Hi there!
		Your OTP for Send Money to Users :'''  + str(request.session['senderotp'])+'''.

		Thanks!'''
			EmailMessage('AVPL - OTP for Send Money to Users', msg, to=[request.user.email]).send()
			print(request.user.email)
			messages.success(request, 'OTP sent successfully.')
			return render(request,'admin_app/otpverifysendmoneytousers.html')
			
		else:
			messages.error(request,'Payments Transaction has been block by Admin,For Re-Activate your payment transaction please contact to Admin.')
			return redirect("/admins/dashboard")
			
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

login_required('/')
@transaction.atomic
@csrf_exempt
def sendmoneytransfer_admin(request):
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
		print(senderotp)
		
		if senderotp == request.session['senderotp']:
			print('hjhjjjjjjjjjjjj')
		
			send_profit_to_users()	
			messages.success(request,'Successfully Transfered')
			return redirect('/admins/dashboard')

		else :
			messages.error(request,'OTP is not Correct')
			return redirect('sendmoneyotpvalidations')

	return render(request,'admin_app/otpverifysendmoneytousers.html')



@csrf_exempt
def admin_bussiness_main_categories(request):
	if check_user_authentication(request, 'ADMIN'):
		
		
		dic = {
			'data': BusinessMainCategory.objects.all().order_by("-id"),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_bussiness_main_categories(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			title= request.POST.get('title')
	
			if title:
				bussinessmaincateobj=BusinessMainCategory.objects.create(title=title)			
				bussinessmaincateobj.updatedby=request.user
				bussinessmaincateobj.save()
				return redirect("/admins/bussiness-main-categories")
		
		dic = {
			'data':BusinessMainCategory.objects.all(),
			'bussinessmaincategories':BusinessMainCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_bussiness_main_categories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=BusinessMainCategory.objects.filter(id=id).first()
		if request.method == 'POST':
			title= request.POST.get('title')
			isactive= request.POST.get('isactive')
			print(title,isactive,'isactiveisactiveisactiveisactive')
			if title:
				bussinessmaincateobj.title=title
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/bussiness-main-categories")
			
		dic = {
			'data':BusinessMainCategory.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_bussiness_main_categories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=BusinessMainCategory.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/bussiness-main-categories")
			
		dic = {
			'data':BusinessMainCategory.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_bussiness_categories(request):
	if check_user_authentication(request, 'ADMIN'):
		
		dic = {
			'data':BusinessCategory.objects.all(),
			'bussinessmaincategories':BusinessMainCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_add_bussiness_categories(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			title= request.POST.get('title')
			main_id= request.POST.get('main_id')
			if title and main_id :
				bussinessmaincateobj=BusinessCategory.objects.create(businessmaincategory=BusinessMainCategory.objects.get(id=main_id),title=title)			
				bussinessmaincateobj.updatedby=request.user
				bussinessmaincateobj.save()
				return redirect("/admins/bussiness-categories")
		
		dic = {
			'data':BusinessMainCategory.objects.all(),
			'bussinessmaincategories':BusinessMainCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_bussiness_categories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=BusinessCategory.objects.filter(id=id).first()
		if request.method == 'POST':
			title= request.POST.get('title')
			main_id= request.POST.get('main_id')
			isactive= request.POST.get('isactive')
			if main_id:
				bussinessmaincateobj.businessmaincategory=BusinessMainCategory.objects.get(id=main_id)				
			if title:
				bussinessmaincateobj.title=title
			if isactive:
				
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/bussiness-categories")
			
		dic = {
			'data':BusinessCategory.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_bussiness_categories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=BusinessCategory.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/bussiness-categories")
			
		dic = {
			'data':BusinessCategory.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/bussiness/bussiness-main-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





@csrf_exempt
def admin_product_brands(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':Brand.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-brands.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_brands(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			title= request.POST.get('title')
			image=request.FILES.get('image')

			if title:
				bussinessmaincateobj=Brand.objects.create(name=title)			
				bussinessmaincateobj.updatedby=request.user
			if image:
				bussinessmaincateobj.image=image
			if title:
				bussinessmaincateobj.save()
				return redirect("/admins/product-brands")
			
		dic = {
			'data':Brand.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-brands.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_brands(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=Brand.objects.filter(id=id).first()
		if request.method == 'POST':
			title= request.POST.get('title')
			isactive= request.POST.get('isactive')
			image=request.FILES.get('image')

			print(title,isactive,'isactiveisactiveisactiveisactive')
			if title:
				bussinessmaincateobj.name=title
			if image:
				bussinessmaincateobj.image=image
                
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-brands")
			
		dic = {
			'data':Brand.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-brands.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_brands(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=Brand.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-brands")
			
		dic = {
			'data':Brand.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-brands.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





@csrf_exempt
def admin_product_units(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':Unit.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_units(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			name= request.POST.get('name')
			symbol=request.POST.get('symbol')

			if name:
				bussinessmaincateobj=Unit.objects.create(name=name)			
				bussinessmaincateobj.updatedby=request.user
			if symbol:
				bussinessmaincateobj.symbol=symbol
			if name:
				bussinessmaincateobj.save()
				return redirect("/admins/product-units")
			
		dic = {
			'data':Unit.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_units(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=Unit.objects.filter(id=id).first()
		if request.method == 'POST':
			name= request.POST.get('name')
			symbol= request.POST.get('symbol')
			isactive= request.POST.get('isactive')
			print(symbol,isactive,'isactiveisactiveisactiveisactive')
			if name:
				bussinessmaincateobj.name=name
			if symbol:
				bussinessmaincateobj.symbol=symbol
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-units")
			
		dic = {
			'data':Unit.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_units(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=Unit.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-units")
			
		dic = {
			'data':Unit.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def admin_product_firstvariant(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':FirstVariant.objects.all(),
   	        'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-firstvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_firstvariant(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			name= request.POST.get('name')
			category_id= request.POST.get('category_id')
			print(category_id,name,'hhghgjjgjgjjh')

			if name and category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj=FirstVariant.objects.create(name=name,category=productobj)			
				bussinessmaincateobj.updatedby=request.user
			
			if name and category_id:
				bussinessmaincateobj.save()
				return redirect("/admins/product-firstvariant")
			
		dic = {
			'data':FirstVariant.objects.all(),
            'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-firstvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_firstvariant(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=FirstVariant.objects.filter(id=id).first()
		if request.method == 'POST':
			name= request.POST.get('name')
			category_id= request.POST.get('category_id')			
			isactive= request.POST.get('isactive')
			
			if name:
				bussinessmaincateobj.name=name
			if category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj.category=productobj
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-firstvariant")
			
		dic = {
			'data':FirstVariant.objects.all(),
		    'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-firstvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_firstvariant(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=FirstVariant.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-firstvariant")
			
		dic = {
			'data':FirstVariant.objects.all(),
   	        'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_product_firstvariantvalue(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':FirstVariantValue.objects.all(),
            'firstvariantobj':FirstVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-firstvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_firstvariantvalue(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			firstvariant_id= request.POST.get('firstvariant_id')
			value=request.POST.get('value')

			if firstvariant_id and value:
				firstvariantobj =FirstVariant.objects.filter(id=firstvariant_id).first()			
				bussinessmaincateobj=FirstVariantValue.objects.create(firstvariant=firstvariantobj,value=value)			
				bussinessmaincateobj.updatedby=request.user

			if firstvariant_id and value:
				bussinessmaincateobj.save()
				return redirect("/admins/product-firstvariantvalue")
			
		dic = {
			'data':FirstVariantValue.objects.all(),
            'firstvariantobj':FirstVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-firstvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_firstvariantvalue(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=FirstVariantValue.objects.filter(id=id).first()
		if request.method == 'POST':
			firstvariant_id= request.POST.get('firstvariant_id')
			value=request.POST.get('value')
			isactive= request.POST.get('isactive')
   
			if firstvariant_id:
				firstvariantobj =FirstVariant.objects.filter(id=firstvariant_id).first()			
				bussinessmaincateobj.firstvariant=firstvariantobj	
				bussinessmaincateobj.updatedby=request.user
		
			if value:
				bussinessmaincateobj.value=value
			
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-firstvariantvalue")
			
		dic = {
			'data':FirstVariantValue.objects.all(),
			'firstvariantobj':FirstVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-firstvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_firstvariantvalue(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=FirstVariantValue.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-firstvariantvalue")
			
		dic = {
			'data':FirstVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





@csrf_exempt
def admin_product_secondvariant(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':SecondVariant.objects.all(),
   	        'productcategory':ProductCategory.objects.all(),
            'sencondchocice':Sencondchocice,
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-secondvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_secondvariant(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			name= request.POST.get('name')
			category_id= request.POST.get('category_id')
			print(category_id,name,'hhghgjjgjgjjh')

			if name and category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj=SecondVariant.objects.create(name=name,category=productobj)			
				bussinessmaincateobj.updatedby=request.user
			
			if name and category_id:
				bussinessmaincateobj.save()
				return redirect("/admins/product-secondvariant")
			
		dic = {
			'data':SecondVariant.objects.all(),
            'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-secondvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_secondvariant(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=SecondVariant.objects.filter(id=id).first()
		if request.method == 'POST':
			name= request.POST.get('name')
			category_id= request.POST.get('category_id')			
			isactive= request.POST.get('isactive')
			
			if name:
				bussinessmaincateobj.name=name
			if category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj.category=productobj
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-secondvariant")
			
		dic = {
			'data':SecondVariant.objects.all(),
		    'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-secondvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_secondvariant(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=SecondVariant.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-secondvariant")
			
		dic = {
			'data':SecondVariant.objects.all(),
   	        'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_product_secondvariantvalue(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':SecondVariantValue.objects.all(),
            'secondvariantobj':SecondVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-secondvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_secondvariantvalue(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			secondvariant_id= request.POST.get('secondvariant_id')
			value=request.POST.get('value')

			if secondvariant_id and value:
				secondvariantobj =SecondVariant.objects.filter(id=secondvariant_id).first()			
				bussinessmaincateobj=SecondVariantValue.objects.create(secondvariant=secondvariantobj,value=value)			
				bussinessmaincateobj.updatedby=request.user

			if secondvariant_id and value:
				bussinessmaincateobj.save()
				return redirect("/admins/product-secondvariantvalue")
			
		dic = {
			'data':SecondVariantValue.objects.all(),
            'secondvariantobj':SecondVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-secondvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_secondvariantvalue(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=SecondVariantValue.objects.filter(id=id).first()
		if request.method == 'POST':
			secondvariant_id= request.POST.get('secondvariant_id')
			value=request.POST.get('value')
			isactive= request.POST.get('isactive')
   
			if secondvariant_id:
				secondvariantobj =SecondVariant.objects.filter(id=secondvariant_id).first()			
				bussinessmaincateobj.secondvariant=secondvariantobj	
				bussinessmaincateobj.updatedby=request.user
		
			if value:
				bussinessmaincateobj.value=value
			
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-secondvariantvalue")
			
		dic = {
			'data':SecondVariantValue.objects.all(),
			'secondvariantobj':SecondVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-secondvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_secondvariantvalue(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=SecondVariantValue.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-secondvariantvalue")
			
		dic = {
			'data':SecondVariantValue.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-secondvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_product_thirdvariant(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':ThirdVariant.objects.all(),
   	        'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-thirdvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_thirdvariant(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			name= request.POST.get('name')
			category_id= request.POST.get('category_id')
			print(category_id,name,'hhghgjjgjgjjh')

			if name and category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj=ThirdVariant.objects.create(name=name,category=productobj)			
				bussinessmaincateobj.updatedby=request.user
			
			if name and category_id:
				bussinessmaincateobj.save()
				return redirect("/admins/product-thirdvariant")
			
		dic = {
			'data':ThirdVariant.objects.all(),
            'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-thirdvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_thirdvariant(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=ThirdVariant.objects.filter(id=id).first()
		if request.method == 'POST':
			name= request.POST.get('name')
			category_id= request.POST.get('category_id')			
			isactive= request.POST.get('isactive')
			
			if name:
				bussinessmaincateobj.name=name
			if category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj.category=productobj
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-thirdvariant")
			
		dic = {
			'data':ThirdVariant.objects.all(),
		    'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-thirdvariant.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_thirdvariant(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=ThirdVariant.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-thirdvariant")
			
		dic = {
			'data':ThirdVariant.objects.all(),
   	        'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-units.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_product_thirdvariantvalue(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':ThirdVariantValue.objects.all(),
            'thirdvariantobj':ThirdVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-thirdvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_thirdvariantvalue(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			thirdvariant_id= request.POST.get('thirdvariant_id')
			value=request.POST.get('value')

			if thirdvariant_id and value:
				thirdvariantobj =ThirdVariant.objects.filter(id=thirdvariant_id).first()			
				bussinessmaincateobj=ThirdVariantValue.objects.create(thirdvariant=thirdvariantobj,value=value)			
				bussinessmaincateobj.updatedby=request.user

			if thirdvariant_id and value:
				bussinessmaincateobj.save()
				return redirect("/admins/product-thirdvariantvalue")
			
		dic = {
			'data':ThirdVariantValue.objects.all(),
            'thirdvariantobj':ThirdVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-thirdvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_thirdvariantvalue(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=ThirdVariantValue.objects.filter(id=id).first()
		if request.method == 'POST':
			thirdvariant_id= request.POST.get('thirdvariant_id')
			value=request.POST.get('value')
			isactive= request.POST.get('isactive')
   
			if thirdvariant_id:
				thirdvariantobj =ThirdVariant.objects.filter(id=thirdvariant_id).first()			
				bussinessmaincateobj.thirdvariant=thirdvariantobj	
				bussinessmaincateobj.updatedby=request.user
		
			if value:
				bussinessmaincateobj.value=value
			
				
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-thirdvariantvalue")
			
		dic = {
			'data':ThirdVariantValue.objects.all(),
			'thirdvariantobj':ThirdVariant.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-thirdvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_thirdvariantvalue(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=ThirdVariantValue.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-thirdvariantvalue")
			
		dic = {
			'data':ThirdVariantValue.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-thirdvariantvalue.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_product_categories(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_categories(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			title= request.POST.get('title')
			image=request.FILES.get('image')

			if title:
				bussinessmaincateobj=ProductCategory.objects.create(name=title)			
				bussinessmaincateobj.updatedby=request.user
			if image:
				bussinessmaincateobj.image=image
			if title:
				bussinessmaincateobj.save()
				return redirect("/admins/product-categories")
			
		dic = {
			'data':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_categories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=ProductCategory.objects.filter(id=id).first()
		if request.method == 'POST':
			title= request.POST.get('title')
			isactive= request.POST.get('isactive')
			image=request.FILES.get('image')

			print(title,isactive,'isactiveisactiveisactiveisactive')
			if title:
				bussinessmaincateobj.name=title
			if image:
				bussinessmaincateobj.image=image
                
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-categories")
			
		dic = {
			'data':ProductCategory.objects.all(),
			
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_categories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=ProductCategory.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-categories")
			
		dic = {
			'data':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
   
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





@csrf_exempt
def admin_product_subcategories(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
            'data':ProductSubCategory.objects.all(),
			'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-subcategory.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_subcategories(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			title= request.POST.get('title')
			category_id= request.POST.get('category_id')
			image=request.FILES.get('image')
			
			if title and category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj=ProductSubCategory.objects.create(name=title,category=productobj)			
			if image:
				bussinessmaincateobj.image=image
			if title and category_id:
				bussinessmaincateobj.updatedby=request.user
				bussinessmaincateobj.save()
				return redirect("/admins/product-subcategories")
		
		dic = {
			'data':ProductSubCategory.objects.all(),
			'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_subcategories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=ProductSubCategory.objects.filter(id=id).first()
		if request.method == 'POST':
			title= request.POST.get('title')
			isactive= request.POST.get('isactive')
			print(title,isactive,'isactiveisactiveisactiveisactive')
			category_id= request.POST.get('category_id')
			image=request.FILES.get('image')
			
			if category_id:
				productobj=ProductCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj.category=productobj		
			if image:
				bussinessmaincateobj.image=image
            
			if title:
				bussinessmaincateobj.name=title
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-subcategories")
			
		dic = {
			'data':ProductSubCategory.objects.all(),
			'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_subcategories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=ProductSubCategory.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-categories")
			
		dic = {
			'data':ProductSubCategory.objects.all(),
			'productcategory':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_product_subsubcategories(request):    
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'data': ProductSubSubCategory.objects.all(),
			'productcategory':ProductSubCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/product/product-sub-subcategory.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_product_subsubcategories(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			title= request.POST.get('title')
			category_id= request.POST.get('category_id')
			image=request.FILES.get('image')
			
			if title and category_id:
				productobj=ProductSubCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj=ProductSubSubCategory.objects.create(name=title,subcategory=productobj)			
			if image:
				bussinessmaincateobj.image=image
			if title and category_id:		
				bussinessmaincateobj.updatedby=request.user
				bussinessmaincateobj.save()
				return redirect("/admins/product-sub-subcategories")
		
		dic = {
			'data': ProductSubSubCategory.objects.all(),
			'productcategory':ProductSubCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-sub-subcategory.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_subsubcategories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		bussinessmaincateobj=ProductSubSubCategory.objects.filter(id=id).first()
		if request.method == 'POST':
			title= request.POST.get('title')
			isactive= request.POST.get('isactive')
			category_id= request.POST.get('category_id')
			image=request.FILES.get('image')
			
			if category_id:
				productobj=ProductSubCategory.objects.filter(id=category_id).first()	
				bussinessmaincateobj.subcategory=productobj	
			if image:
				bussinessmaincateobj.image=image

			if title:
				bussinessmaincateobj.name=title
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				bussinessmaincateobj.isactive=isactive
			else:
				isactive=False	
				bussinessmaincateobj.isactive=isactive
             
			bussinessmaincateobj.updatedby=request.user
			bussinessmaincateobj.save()
			return redirect("/admins/product-sub-subcategories")
			
		dic = {
			'data': ProductSubSubCategory.objects.all(),
			'productcategory':ProductSubCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-sub-subcategory.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_product_subsubcategories(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			bussinessmaincateobj=ProductSubSubCategory.objects.filter(id=id).first()
			bussinessmaincateobj.delete()
			return redirect("/admins/product-sub-subcategories")
			
		dic = {
			'data': ProductSubSubCategory.objects.all(),
			'productcategory':ProductSubCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-sub-subcategory.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_product(request):
	if check_user_authentication(request, 'ADMIN'):
		product = Product.objects.get(id=request.GET.get('id'))
		dic = {
			'product':product,
			'images':ProductImages.objects.filter(product=product),
			'variants':ProductVariants.objects.filter(product=product),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request,'admin_app/product/product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_product_approval(request):
	if check_user_authentication(request, 'ADMIN'):
		
		# if request.method == 'POST':
		# 	id = request.POST.get('id')
		# 	vendor_commission = request.POST.get('vendor_commission')
		# 	prod=Product.objects.filter(id=id).first()
		# 	prod.vendor_commission = vendor_commission
		# 	prod.save()
		# 	messages.success(request, 'New Vendor Commission has been set. ! ')
		# 	return redirect('/admins/product-approval')
		
		dic = {'data':ProductVariants.objects.filter(isactive=False, product__isproductrejected=False),
			'rejected_product':ProductVariants.objects.filter(isactive=False, product__isproductrejected=True),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product-approval.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def admin_product_list(request):
	if check_user_authentication(request, 'ADMIN'):
		
		dic = {
			'products':Product.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/product/product_list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def admin_edit_product(request,id):
	if check_user_authentication(request, 'ADMIN'):
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
					productname = productname
				if description:
					description = description
					
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
				if hsn:
					pro.tax= tax
				if hsn:
					pro.pv =pv
				if hsn:
					pro.admincommission =admincommission

				pro.save()
				messages.success(request,f'Product {productname} is updated Successfully')
				return redirect('/admins/all-products')
			else:
				messages.info(request, f'Please fill all detials such as productname and category !')
				return redirect('/admins/all-products')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

	

@csrf_exempt
def admin_product_variants_list(request,id):
	if check_user_authentication(request, 'ADMIN'):
	
		dic = {
			'categories':ProductCategory.objects.filter(),
			'subcategories':ProductSubCategory.objects.filter(),
			'subsubcategories':ProductSubSubCategory.objects.filter(),
            'units':Unit.objects.filter(),
			'brands':Brand.objects.filter(),
			'firstvariantvalue':FirstVariantValue.objects.filter(firstvariant__category__id=id),
			'secondvariantvalue':SecondVariantValue.objects.filter(secondvariant__category__id=id),
			'thirdvariantvalue':ThirdVariantValue.objects.filter(thirdvariant__category__id=id),
			'products':Product.objects.filter(id=id).first(),
            'product_variants':ProductVariants.objects.filter(product__id=id),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/product/product-variants-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_product_variants(request,id):
	if check_user_authentication(request, 'ADMIN'):
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
	
			if ProductVariants.objects.filter(id=id).exists():
				productvariantsobj=ProductVariants.objects.filter(id=id).first()
	
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
				
				productvariantsobj.save()
				messages.success(request,f'Product Variants {productvariantname} is updated Successfully')
				return redirect(f'/admins/product-variants-list/{productvariantsobj.product.id}')
			else:
				pass
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')







@csrf_exempt
def admin_vendor_verification(request):
	if check_user_authentication(request, 'ADMIN'):
		vendor=Vendor.objects.filter(docsubmitted=True, verified=False)
		print(vendor,'VVVVVVVVVVVVVvv')

		dic = {
			'categories':ProductCategory.objects.all(),
			'data':Store.objects.filter(vendor__docsubmitted=True, vendor__verified=False),
			# 'notification':get_notifications(request.user,'ADMIN'),
			# 'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/store/vendor_verification.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_vendor_list(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'data':Vendor.objects.filter(docsubmitted=True, verified=True),
			# 'notification':get_notifications(request.user,'ADMIN'),
			# 'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/store/vendor_list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_is_activate_approved_avpl_vendor(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(isavplvendor=True)
		sub = 'AVPL -AVPL Vendor Approved Successfully'
		msg = '''Hi there!
Your AVPL Vendor Approved Successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Approved Successfully !!!!')
		# notification(request.user, 'Vendor '+vendor.firstname+' '+vendor.lastname)
		# notification(vendor.user, 'AVPL Vendor Approved Successfully.')
		return redirect('/admins/store/vendor-list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_is_deactivate_approved_avpl_vendor(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(isavplvendor=False)
		sub = 'AVPL -AVPL Vendor Deactivate Successfully'
		msg = '''Hi there!
Your AVPL Vendor Deactivate Successfully.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Deactivate Successfully !!!!')
		# notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		# notification(vendor.user, 'AVPL Vendor Deactivate Successfully.')
		return redirect('/admins/store/vendor-list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_vendor_profile(request):
	if check_user_authentication(request, 'ADMIN'):
		vendor = Vendor.objects.get(id=request.GET.get('i'))
		store = Store.objects.get(vendor=vendor)
		businessmaincategory_obj=BusinessMainCategory.objects.filter(isactive=True)
		businesscategory_obj=BusinessCategory.objects.filter(isactive=True)
		
		dic = {
			'storeobj':store,
			'vendor':vendor,
            "businessmaincategory_obj":businessmaincategory_obj,
			"businesscategory_obj":businesscategory_obj,
			'categories':ProductCategory.objects.all()
		}
		return render(request,'admin_app/store/vendor-profile.html', dic)
	else:
		return HttpResponse('Error 500 : Unauthorized User')



@csrf_exempt
def admin_edit_vendor_profile(request):
	if check_user_authentication(request, 'ADMIN'):
		id=request.GET.get('i')
		vendor = Vendor.objects.get(id=id)
		
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
    
			
		
			vendor_obj=vendor
			
			user=User.objects.filter(id=vendor_obj.user.id).first()
	
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

			messages.info(request, 'Vendor Profile has been updated !')

		return redirect(f"/admins/vendorprofile?i={id}")
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_activate_approved_avpl_vendor(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(isavplvendor=True)
		sub = 'AVPL -AVPL Vendor Approved Successfully'
		msg = '''Hi there!
Your AVPL Vendor Approved Successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Approved Successfully !!!!')
		# notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		# notification(vendor.user, 'AVPL Vendor Approved Successfully.')
		return redirect('/admins/store/kycrequests')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_activate_vendor(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(verified=True)
		sub = 'AVPL - Vendor Account Activated Successfully'
		msg = '''Hi there!
Your AVPL Vendor Account has been activated successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'Vendor Activated Successfully !!!!')
		# notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		# notification(vendor.user, 'Profile Activated Successfully.')
		return redirect('/admins/store/vendor-verification')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')






@csrf_exempt
def admin_vendor_commission_wallet(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'vendor_commission_wallet':CommissionWallet.objects.filter(vendor__storecreated=True), 
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/store/vendor_commission_wallet.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_vendor_commission_wallet_details(request, id):
	if check_user_authentication(request, 'ADMIN'):

		vendor_commission_wallet=CommissionWallet.objects.filter(id=id).first()
		vendor_commission_wallet_transaction = CommissionWalletTransaction.objects.filter(commissionwallet=vendor_commission_wallet)
		dic = {
            'vendor_commission_wallet':vendor_commission_wallet,
			'vendor_commission_wallet_transaction':vendor_commission_wallet_transaction,
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		
		}
		return render(request, 'admin_app/store/wallet_commission_dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_activate_is_commission_wallet_vendor(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		wallet = CommissionWallet.objects.get(id=id_)
		CommissionWallet.objects.filter(id=id_).update(isactive=True)
		sub = 'AVPL -Vendor Commission wallet activated Successfully'
		msg = '''Hi there!
Your AVPL Vendor Commission wallet activated Successfully, you can transaction.

Thanks!'''
		EmailMessage(sub,msg,to=[wallet.vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Commission wallet activated Successfully !!!!')
		# notification(request.user, 'Vendor '+wallet.vendor.firstname+' '+wallet.vendor.lastname)
		# notification(wallet.user, 'AVPL Vendor Commission wallet activated Successfully.')
		return redirect('/admins/vendor-commission-wallet')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_deactivate_is_commission_wallet_vendor(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		wallet = CommissionWallet.objects.get(id=id_)
		CommissionWallet.objects.filter(id=id_).update(isactive=False)
		sub = 'AVPL -AVPL Vendor Commission wallet Deactivate Successfully'
		msg = '''Hi there!
Your AVPL Vendor Commission wallet Deactivate Successfully.

Thanks!'''
		EmailMessage(sub,msg,to=[wallet.vendor.user.email]).send()
		messages.success(request, 'AVPLVendor Commission wallet Deactivate Successfully !!!!')
		# notification(request.user, 'Vendor '+wallet.vendor.firstname+' '+wallet.vendor.lastname)
		# notification(wallet.user, 'AVPL Vendor Commission wallet Deactivate Successfully.')
		return redirect('/admins/vendor-commission-wallet')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')









@csrf_exempt
def admin_pv_wallet(request):
	if check_user_authentication(request, 'ADMIN'):
		print(request.user)
		dic = {'user':UserData.objects.get(user=request.user),
			'pv':fetch_pv(request.user),
			'transactions':fetch_pv_transactions(request.user),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pv.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_point_value(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'GET':
			c=request.GET.get('c')
			category = ProductCategory.objects.get(id =c )
			dic = {'categories':ProductCategory.objects.all(), 'point':PointValue.objects.get(category=category)}
			return render(request,'admin_app/point-value.html', dic)
		elif request.method == 'POST':
			new = request.POST.get('new')
			id_ = request.POST.get('category')
			category = ProductCategory.objects.get(id = id_)
			PointValue.objects.filter(category=category).update(percentage=new)
			messages.success(request, 'Point Value Percentage Updated Successfully !!!!')
			notification(request.user, 'PV of '+category.name+' set to '+ str(PointValue.objects.get(category=category).percentage))
			return redirect('/admins/point/?c='+id_)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_create_link(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/create-link.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def wallet_details(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'wallet':Wallet.objects.filter(user__is_superuser=True),'categories':ProductCategory.objects.all(),
			'wallettransactions':WalletTransaction.objects.filter(wallet__user__is_superuser=True),
			# 'wallettransactions':WalletTransaction.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False))
	    	}
		return render(request, 'admin_app/wallet.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_wallet_recharge(request):
	if check_user_authentication(request, 'ADMIN'):
		if not Wallet.objects.filter(user=request.user).exists():
			Wallet.objects.create(user=request.user)

		wallet=Wallet.objects.filter(user__is_superuser=True).first()
		if request.method == 'POST':
			amoun = request.POST.get('amount')
			amount = float(amoun)

			WalletTransaction.objects.create(
			wallet = wallet,
			transaction_date = timezone.now(),
			transaction_type = 'CREDIT',
			transaction_amount = amount,
			previous_amount = round(wallet.current_balance, 2) if wallet.current_balance else 0 ,
			remaining_amount = round(wallet.current_balance,2) + round(amount,2)
			)
			wallet=Wallet.objects.filter(user__is_superuser=True).update(current_balance = round(wallet.current_balance, 2) + round(amount, 2))		
				
			return redirect('/admins/wallet_details')

		dic = {'wallet':Wallet.objects.filter(user__is_superuser=True),'categories':ProductCategory.objects.all(),
			'wallettransactions':WalletTransaction.objects.filter(wallet__user__is_superuser=True),'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),}
		return render(request, 'admin_app/wallet.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_generate_link_left(request):
	if check_user_authentication(request, 'ADMIN'):
		data = {'link':generate_link(request.user, 'Admin','left')}
		# messages.success(request, 'You have been generated left link !')
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})
@csrf_exempt
def admin_generate_link_right(request):
	if check_user_authentication(request, 'ADMIN'):
		data = {'link':generate_link(request.user, 'Admin','right')}
		# messages.success(request, 'You have been generated right link !')
		return JsonResponse(data)
		
	else:
		return JsonResponse({'response':'Error'})

@csrf_exempt
def admin_under_trees(request):
	if check_user_authentication(request, 'ADMIN'):
		print(request.user)
		
        
		for users in MLMAdmin.objects.all():
			child=users.child
			print(fetch_user_tree(child),'TTTTTTTTTTt')

		dic = {'data':MLMAdmin.objects.all(), 'categories':ProductCategory.objects.all(),
		'tree':fetch_user_tree(child),
		'notification':get_notifications(request.user,'ADMIN'),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/under-trees.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_under_trees_level(request):
	if check_user_authentication(request, 'ADMIN'):
		referal_obj = Level_Plan_Referrals.objects.filter(referrals__id=request.user.id).first()
		referals = Level_Plan_Referrals.objects.filter(level_plan_referral=referal_obj)
		dic = {'data':referals, 'categories':ProductCategory.objects.all(),}
		return render(request, 'admin_app/under-trees-level.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def genealogyTree_binary(request):
	if check_user_authentication(request, 'ADMIN'):

		for users in MLMAdmin.objects.all():
			child=users.child
			print(fetch_user_tree(child),'TTTTTTTTTTt')
		tree=fetch_user_tree(child)
		treesss=fetch_empty_nodes(child)
		print(treesss,'TTTT')
		print(treesss['left'],'LLLLLLLLLLLLLLLLLLLLLLLLLL')
		print(treesss['right'],'RRRRRRRRRRRRRRRRRRRRRRRRR')

		# count = 0
		for userl in treesss['left']:
			# if count < 1:
			left_empty=fetch_empty_nodesmlmleft(userl)
			for user in left_empty['left']:
				print(user,'LeftlllllllLLLL')
				# count += 1

		count = 0
		for userr in treesss['right']:
			if count < 1:
				right_empty=fetch_empty_nodesmlmright(userr)
				for user in right_empty['right']:
					print(user,'RightlllllllLLLL')
				count += 1
	
		
		node=MLM.objects.filter(node=child)
		node_V=MLM.objects.filter(node=child).first()
		
		usrpv = UserPV.objects.get(user=child)
		if node_V.left  is not None:
			nodel=MLM.objects.filter(node=node_V.left)
			for x in nodel:
				print(x.left,'XXXXLLLLLL')
			usrpvl = UserPV.objects.get(user=node_V.left)
			noder=MLM.objects.filter(node=node_V.right)
		if node_V.right is not None:
			usrpvr = UserPV.objects.get(user=node_V.right)
		else:
			print('None')
		
		if request.method == "POST":
			
			user1 = request.POST.get('user1')
			user2 = request.POST.get('user2')
			user3 = request.POST.get('user3')
			user4 = request.POST.get('user4')
			
			# print(user,'lllUUUUUU')
			nodes1=MLM.objects.filter(node__email=user1)
			print(nodes1,'NNNNN')
			nodes_v1=MLM.objects.filter(node__email=user1).first()
			if nodes_v1 is not None:
				if nodes_v1.left and nodes_v1.right is not None:
					usrpvsl1 = UserPV.objects.get(user__email=nodes_v1.left)
					usrpvsr1 = UserPV.objects.get(user__email=nodes_v1.right)
				else:
				    print('None')	
			else:
				print('None')
			nodes2=MLM.objects.filter(node__email=user2)
			nodes_v2=MLM.objects.filter(node__email=user2).first()
			if nodes_v2 is not None:
				if nodes_v2.left and nodes_v2.right is not None:
					try:
					   usrpvsl2 = UserPV.objects.get(user__email=nodes_v2.left)
					except UserPV.DoesNotExist:
						usrpvsl2 = None
					try:
					    usrpvsr2 = UserPV.objects.get(user__email=nodes_v2.right)
					except UserPV.DoesNotExist:
						usrpvsr2 = None
				else:
				    print('None')
			else:
				print('None')

			nodes3=MLM.objects.filter(node__email=user3)
			nodes_v3=MLM.objects.filter(node__email=user3).first()
			if nodes_v3 is not None:
				if nodes_v3.left and nodes_v3.right is not None:
					usrpvsl3 = UserPV.objects.get(user__email=nodes_v3.left)
					usrpvsr3 = UserPV.objects.get(user__email=nodes_v3.right)
				else:
					print('None')	
			else:
				print('None')
			nodes4=MLM.objects.filter(node__email=user4)
			nodes_v4=MLM.objects.filter(node__email=user4).first()
			if nodes_v4 is not None:
				if nodes_v4.left and nodes_v4.right is not None:
					try:
						usrpvsl4 = UserPV.objects.get(user__email=nodes_v4.left)
					except UserPV.DoesNotExist:
						usrpvsl4 = None
					try:
						usrpvsr4 = UserPV.objects.get(user__email=nodes_v4.right)
					except UserPV.DoesNotExist:
						usrpvsr4 = None
				else:
					print('None')
			else:
				print('None')

		
			if nodes_v1 and nodes_v2 and nodes_v3 and nodes_v4 is not None:
				if nodes_v1.left and nodes_v1.right or  nodes_v2.left and nodes_v2.right or  nodes_v3.left and nodes_v3.right or  nodes_v4.left and nodes_v4.right  is not None:
					dic = {
						'user':UserData.objects.get(user=child),
						'tree':fetch_user_tree(child),
						'nodel':nodel,
						'noder':noder,
						'trees':node,
						'nodes1':nodes1,
						'nodes2':nodes2,
						'nodes3':nodes3,
						'nodes4':nodes4,
						'usrpvsl1':usrpvsl1,
						'usrpvsl2':usrpvsl2,
						'usrpvsl3':usrpvsl3,
						'usrpvsl4':usrpvsl4,
						'usrpvsr1':usrpvsr1,
						'usrpvsr2':usrpvsr2,
						'usrpvsr3':usrpvsr3,
						'usrpvsr4':usrpvsr4,

						'child':child,
						'notification':get_notifications(request.user,'ADMIN'),
						'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
							}
				else:
					print('None')
					dic = {
					'user':UserData.objects.get(user=child),
					'tree':fetch_user_tree(child),
					'nodel':nodel,
					'noder':noder,
					'trees':node,
					'nodes1':nodes1,
					'nodes2':nodes2,
					'nodes3':nodes3,
					'nodes4':nodes4,
				
					
					
					'child':child,
					'notification':get_notifications(request.user,'ADMIN'),
					'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
						}
			else:
				print('None')
				dic = {
					'user':UserData.objects.get(user=child),
					'tree':fetch_user_tree(child),
					'nodel':nodel,
					'noder':noder,
					'trees':node,

					'nodes1':nodes1,
					'nodes2':nodes2,
					'nodes3':nodes3,
					'nodes4':nodes4,
					
					
					
					'child':child,
					'notification':get_notifications(request.user,'ADMIN'),
					'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
						}
			return render(request, 'admin_app/genealogyTree_binary.html',dic)
		if node_V.left  is not None:	
			return render(request, 'admin_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv,'usrpvl':usrpvl,'nodel':nodel,
						'noder':noder,})
		
		if node_V.right is not None:					
		    return render(request, 'admin_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv,'usrpvr':usrpvr,
						})
		else:
			print('None')
			return render(request, 'admin_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv})
	else:
		return render(request, '403.html')

@csrf_exempt
def genealogyTree_level(request):
	if check_user_authentication(request, 'ADMIN'):
		for child in Level_Plan_Referrals.objects.filter(level_plan_sponsor__id=request.user.id):
			print(child)
		referal_obj = Level_Plan_Referrals.objects.filter(referrals__id=request.user.id).first()
		if referal_obj is not None:
		    # print(referal_obj.referrals,"SSSS")
			usrpv = UserPV.objects.get(user__email=referal_obj.referrals)
		else:
			print('None')
		referals = Level_Plan_Referrals.objects.filter(level_plan_referral=referal_obj)
		print(referals,'RRRRRRRRRRr')
		referalss = Level_Plan_Referrals.objects.filter(level_plan_referral=referal_obj).first()
		print(referalss)
		if referalss is not None:
			usrpvs = UserPV.objects.get(user__email=referalss.referrals)

			print(usrpvs,'PPPPPPPPPP')
		else:
			print("None")

		if request.method == "POST":
			
			userss = request.POST.get('userss')
			print(userss,'UUUUUSSSSSSSSSSSSSSSSSS')
			referal_user = Level_Plan_Referrals.objects.filter(referrals__id=userss).first()
			referals_user = Level_Plan_Referrals.objects.filter(level_plan_referral=referal_user)
            
			print(referal_user,referals_user,'RRRRUUUUUUUUUU')
		    
			dic = {
				# 'user':UserData.objects.get(user=request.user),
				'referals':referals,
				# 'sponser_r':referal_obj.referrals,
				# 'notification':get_notifications(request.user,'ADMIN'),
				# 'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
				'referals_user':referals_user,
				
			}
			return render(request, 'admin_app/genealogyTree_level.html',dic)
			
			
		if referal_obj or referalss  is not None:	
			
		
			dic = {
				# 'user':UserData.objects.get(user=request.user),
				'referals':referals,
				# 'sponser_r':referal_obj.referrals,
				# 'notification':get_notifications(request.user,'ADMIN'),
				# 'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}

		
		else:
			print('none')
			dic = {
				# 'user':UserData.objects.get(user=request.user),
				'referals':referals,'usrpvs':usrpvs,
				# 'sponser_r':referal_obj,
				# 'notification':get_notifications(request.user,'ADMIN'),
				# 'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			}
		return render(request, 'admin_app/genealogyTree_level.html',dic)
	else:
		return render(request, '403.html')















@csrf_exempt
def admin_delivery_charges(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			charge = request.POST.get('charge')
			DeliveryCharge.objects.all().delete()
			DeliveryCharge.objects.create(amount=charge)
			messages.success(request, 'Charges Updated Successfully')
			notification(request.user, 'Delivery Charges Changed.')
			return redirect('/admins/deliverycharges')
		dic = {'charge':DeliveryCharge.objects.all(),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/delivery-charges.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_payment_info(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'paymenttransaction':PaymentTransaction.objects.all().order_by('-id'),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/payment-info.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_orders(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'orders':OrderItems.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_pvpairvalue(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			new = request.POST.get('new')
			PVPairValue.objects.all().delete()
			PVPairValue.objects.create(pair_value=new)
			notification(request.user, 'PV Pair Value Changed')
			return redirect('/admins/setpvpair')
		dic = {'data':PVPairValue.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/set-pv-pair.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_withdraw(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {'users':WithdrawRequest.objects.filter().exclude(customer = None), 'vendors':WithdrawRequest.objects.filter().exclude(vendor = None), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/withdraw.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_change_withdraw_status(request):
	if check_user_authentication(request, 'ADMIN'):
		type_ = request.GET.get('t')
		id_ = request.GET.get('i')
		status = request.GET.get('s')
		if type_ == 'CUSTOMER':
			WithdrawRequest.objects.filter(id=id_).update(isactive=status)
			withdraw = WithdrawRequest.objects.get(id=id_)
			if status == '1':
				statuschanges= 'Withdraw request has been approved !.'
			if status == '2':

				Make_TDSLogWallet_Transaction('CUSTOMER', withdraw.customer.user, withdraw.amount, 'CREDIT',withdraw.creditedamount,withdraw.tds)
				make_wallet_transaction('CUSTOMER', withdraw.customer.user, withdraw.amount, 'DEBIT')
				statuschanges= 'Withdraw Amount has been Credited !.'
				# notification(withdraw.user, 'Rs'+str(withdraw.amount)+' debited from your wallet.')
				# notification(withdraw.user, 'Withdraw Request Status Changed.')
			if status == '3':
				statuschanges= 'Withdraw request has been Rejected !.'
				# notification(withdraw.user, 'Withdraw Request Status Changed.')

		elif type_ == 'VENDOR':
        
			WithdrawRequest.objects.filter(id=id_).update(isactive=status)
			withdraw = WithdrawRequest.objects.get(id=id_)
			if status == '1':
				statuschanges= 'Withdraw request has been approved !.'
			if status == '2':
				make_wallet_transaction('VENDOR', withdraw.vendor.user, withdraw.amount, 'DEBIT')
				statuschanges='Withdraw Amout has been Credited !.'
				# notification(withdraw.user, 'Rs'+str(withdraw.amount)+' debited from your wallet.')
				# notification(withdraw.user, 'Withdraw Request Status Changed.')
			if status == '3':
				statuschanges='Withdraw request has been Rejected !.'
				# notification(withdraw.user, 'Rs'+str(withdraw.amount)+' credit to your wallet.')
				# notification(withdraw.user, 'Withdraw Request Status Changed.')

		messages.success(request, statuschanges)
		return redirect('/admins/withdraw')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_query(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {'queries':Query.objects.all().order_by('-id'),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/query.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_query_result(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {'query':Query.objects.get(id=request.GET.get('query_id')),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/query-result.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_change_query_status(request):
	if check_user_authentication(request, 'ADMIN'):
		Query.objects.filter(id=request.GET.get('query')).update(status=request.GET.get('status'))
		user = Query.objects.get(id=request.GET.get('query')).user
		notification(user, 'Query Status Changed.')
		return JsonResponse({'response`	':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
		
@csrf_exempt
def admin_query_send_reply(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method =="POST":
			img_data=request.POST.get('image')
			if img_data:
				format, imgstr = img_data.split(';base64,')
				ext = format.split('/')[-1]
				image_data = ContentFile(base64.b64decode(imgstr), name='reply_image.'+ext)
			else:
				image_data=''
			q_data=Query.objects.get(id=request.POST.get('query'))
			q_data.reply=request.POST.get('reply')
			if image_data:
				q_data.reply_image=image_data

			q_data.save()
			
			# update(
			# 	reply=request.POST.get('reply'),reply_image=image_data
			# )
			query = Query.objects.get(id=request.POST.get('query'))
			if query.reply_image :
				image=query.reply_image
			else:
				image=''
			if query.anonymous:
				msg = '''Hi '''+query.name+''',

	'''+query.reply+''' ,
	'''+image+'''

	Thanks & Regards,
	Team AVPL'''
				EmailMessage('AVPL - Query Reply',msg,to=[query.email]).send()
				return JsonResponse({'response`	':'Success'})
			user = Query.objects.get(id=request.POST.get('query')).user
			notification(user, 'Admin Replied to Your Query')
			return JsonResponse({'response`	':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_set_pv_conversion(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('new')
			PVConversionValue.objects.all().delete()
			PVConversionValue.objects.create(
				conversion_value = value
			)
			notification(request.user, 'User Share Percent Changed.')
			return redirect('/admins/setpvconversion')
		dic = {'data':PVConversionValue.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/set-pv-conversion.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_direct_referal(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('value')
			DirectReferalCommission.objects.all().delete()
			DirectReferalCommission.objects.create(
				percentage=value,
			)
			notification(request.user,'Direct Referal Commission Precent Changed.')
			return redirect('/admins/direct-referal')
		dic = {'data':DirectReferalCommission.objects.all(),
		'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/direct-referal.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_leadership_bonus_set(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('leader')
			target = request.POST.get('target')
			UserLeadershipBonusCommission.objects.all().delete()
			UserLeadershipBonusCommission.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/leadershipbonus')
		dic = {'data':UserLeadershipBonusCommission.objects.all(),
		'notification':get_notifications(request.user,'ADMIN'),
		'leadership_bonus':get_leadership_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/leadership-bonus.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_travel_fund_set(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			TravelFund.objects.all().delete()
			TravelFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/travelfund')
		dic = {'data':TravelFund.objects.all(),
		'notification':get_notifications(request.user,'ADMIN'),
		'travel_fund':get_travel_fund_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/travel-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_car_fund_set(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			CarFund.objects.all().delete()
			CarFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/carfund')
		dic = {'data':CarFund.objects.all(),
		'notification':get_notifications(request.user,'ADMIN'),
		'car_fund':get_car_fund_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/car-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_house_fund_set(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			HouseFund.objects.all().delete()
			HouseFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/housefund')
		dic = {'data':HouseFund.objects.all(),
		'notification':get_notifications(request.user,'ADMIN'),
		'house_fund':get_house_fund_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/house-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_directorship_fund_set(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			DirectorshipFund.objects.all().delete()
			DirectorshipFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/directorshipfund')
		dic = {'data':DirectorshipFund.objects.all(),
		'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
		'directorship_fund':get_directorship_fund_eligible_users(request),
		'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/directorship-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_product_basic_edit(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			
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
				discount= discount
				# isactive= False
			)
			messages.success(request, 'Product Updated Successfully')
			return redirect('/admins/product?id='+request.POST.get('id'))
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_delete_product_image(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'GET':
			ProductImages.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_delete_product_variant(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'GET':
			ProductVariant.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_product_out_of_stock(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'GET':
			Product.objects.filter(id=request.GET.get('i')).update(stock=0)
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_activate_product(request):
	if check_user_authentication(request, 'ADMIN'):
		productvarinatobj=ProductVariants.objects.filter(id=request.GET.get('p')).first()
		productvarinatobj.isactive=True
		productvarinatobj.save()
		proobj=Product.objects.filter(id=productvarinatobj.product.id).first()
		proobj.isactive=True
		proobj.save()
		# notification(vendor, 'Product Activated Successfully.')
		return redirect('/admins/product-approval')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_taxation(request):
	if check_user_authentication(request, 'ADMIN'):
		if len(Tax.objects.all()) == 0 :
			Tax.objects.create(currenttax=0)
			
		tax =Tax.objects.filter().first()
		if request.method == 'POST':
			pay = request.POST.get('pay')
			if tax.currenttax >=  float(pay) and float(pay) != 0  :
				
				TaxPay.objects.create(
					transactiondate = timezone.now(),
					taxcurrent = tax.currenttax,
					taxpaid = pay,
					taxremaining = tax.currenttax - float(pay)
				)
				tax.currenttax = tax.currenttax - float(pay)
				tax.save()
				messages.success(request, 'Tax has been paid sucessfully !')
				return redirect('/admins/tax')
			else:
				messages.warning(request, 'Insufficient balance !')
				return redirect('/admins/tax')
		dic = {'tax':tax, 'transactions':TaxPay.objects.all()}
		return render(request, 'admin_app/tax.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')




@csrf_exempt
def admin_users(request):
	if check_user_authentication(request, 'ADMIN'):
		users = User.objects.filter(isactive=True)
		lt = []
		for x in users :
			print(x,'USSSSSSSSs')
			roles=Role.objects.filter(user=x).first()

			print(roles,'RRRRRRR')
			if x.role.level.level == 'User':
				dic = {'user':x}
				dic.update(get_user_indecater(x))
				dic.update(get_user_wallet(x))
				lt.append(dic)
			elif x.role.level.level == 'Vendor':
				dic = {'user':x}
				dic.update(get_user_wallet(x))
				lt.append(dic)
		print(lt,'List')

		wallets=Wallet.objects.filter(user=x).first()

		print(wallets,'WWWWWWWWWWWWWWWWWwwww')
		
		return render(request, 'admin_app/users.html',{'users':lt,'wallets':wallets})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_users_delete(request):
	if check_user_authentication(request, 'ADMIN'):
		User.objects.filter(id=request.GET.get('i')).delete()
		messages.success(request, 'User Deleted Successfully')
		return redirect('/admins/users')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_commission(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			new = request.POST.get('new')
			Vendor_Commission.objects.all().delete()
			Vendor_Commission.objects.create(percentage=new)
			notification(request.user, 'Vendor Commission Changed')
			return redirect('/admins/vendorcommission')
		dic = {'data':Vendor_Commission.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/set-vendor-commission.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def user_vendor_commission(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			new = request.POST.get('new')
			UserVendorCommission.objects.all().delete()
			UserVendorCommission.objects.create(percentage=new)
			notification(request.user, 'User Vendor Commission Changed')
			return redirect('/admins/uservendorcommission')
		dic = {'data':UserVendorCommission.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/set-user-vendor-commission.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_level_settings(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			levels = int(request.POST.get('levels'))
			groups = int(request.POST.get('groups'))
			if not len(Level_Settings.objects.all()) == 0:
				Level_Settings.objects.all().delete()
			level = Level_Settings.objects.create(
				levels = levels,
				groups = groups
			)
			for x in range(0, level.groups):
				Level_Group.objects.create(level = level)
			messages.success(request, 'Step 1 Configuration Completed Successfully, Please Configure the Level Groups to Complete Configuration')
			return redirect('/admins/settings/')
		levels = Level_Settings.objects.all()
		dic = {}
		if len(levels) > 0:
			count = 1
			lt = []
			for x in Level_Group.objects.filter(level=levels[0]):
				for y in range(0, x.no_of_levels):
					dic = {'level':count, 'percent':x.percent_per_level}
					lt.append(dic)
					count = count + 1
			dic = {'level':levels[0], 'groups':Level_Group.objects.filter(level=levels[0]), 'data':lt, 'data_len': len(lt), 'categories':ProductCategory.objects.all(),}
		return render(request, 'admin_app/level.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_fetch_groups(request):
	if check_user_authentication(request, 'ADMIN'):
		levels = Level_Settings.objects.all()
		dic = {}
		if len(levels) > 0:
			dic = {'level':levels[0], 'groups':Level_Group.objects.filter(level=levels[0]),'categories':ProductCategory.objects.all(),}
		return render(request, 'admin_app/level-table.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_edit_group(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			levels = request.POST.get('levels')
			percent = request.POST.get('percent')
			group = Level_Group.objects.get(id=request.POST.get('group_id'))
			
			total_levels = int(levels)
			total_percent = float(levels)*float(percent)
			for x in Level_Group.objects.filter(level=group.level):
				total_levels = total_levels + x.no_of_levels
				total_percent = total_percent + (x.percent_per_level*x.no_of_levels)
			
			if total_levels > group.level.levels and total_percent > 100.0:
				return JsonResponse({'response':'Failed'})
			else:
				group.no_of_levels = levels
				group.percent_per_level = percent
				group.save()
				return JsonResponse({'response':'Success'})
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_level_settings_level_plan(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			levels = int(request.POST.get('levels'))
			groups = int(request.POST.get('groups'))
			if not len(Level_Settings_Level_Plan.objects.all()) == 0:
				Level_Settings_Level_Plan.objects.all().delete()
			level = Level_Settings_Level_Plan.objects.create(
				levels = levels,
				groups = groups
			)
			for x in range(0, level.groups):
				Level_Group_Level_Plan.objects.create(level = level)
			messages.success(request, 'Step 1 Configuration Completed Successfully, Please Configure the Level Groups to Complete Configuration')
			return redirect('/admins/level/settings/')
		levels = Level_Settings_Level_Plan.objects.all()
		dic = {}
		if len(levels) > 0:
			count = 1
			lt = []
			for x in Level_Group_Level_Plan.objects.filter(level=levels[0]):
				for y in range(0, x.no_of_levels):
					dic = {'level':count, 'percent':x.percent_per_level}
					lt.append(dic)
					count = count + 1
			dic = {'level':levels[0], 'groups':Level_Group_Level_Plan.objects.filter(level=levels[0]), 'data':lt, 'data_len': len(lt),'categories':ProductCategory.objects.all(),}
		return render(request, 'admin_app/level-level_plan.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_fetch_groups_level(request):
	if check_user_authentication(request, 'ADMIN'):
		levels = Level_Settings_Level_Plan.objects.all()
		dic = {}
		if len(levels) > 0:
			dic = {'level':levels[0], 'groups':Level_Group_Level_Plan.objects.filter(level=levels[0]),'categories':ProductCategory.objects.all(),}
		return render(request, 'admin_app/level-table.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_edit_group_level(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			levels = request.POST.get('levels')
			percent = request.POST.get('percent')
			group = Level_Group_Level_Plan.objects.get(id=request.POST.get('group_id'))
			
			total_levels = int(levels)
			total_percent = float(levels)*float(percent)
			for x in Level_Group_Level_Plan.objects.filter(level=group.level):
				total_levels = total_levels + x.no_of_levels
				total_percent = total_percent + (x.percent_per_level*x.no_of_levels)
			
			if total_levels > group.level.levels and total_percent > 100.0:
				return JsonResponse({'response':'Failed'})
			else:
				group.no_of_levels = levels
				group.percent_per_level = percent
				group.save()
				return JsonResponse({'response':'Success'})
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_min_cart_value(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			Min_Amount_For_Free_Delivery.objects.all().delete()
			Min_Amount_For_Free_Delivery.objects.create(amount=amount)
			return redirect('/admins/minmumcartvalue/')
		dic = {'cart':Min_Amount_For_Free_Delivery.objects.get()}
		return render(request, 'admin_app/set-min-cart-value.html', dic)
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_billing_config(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			admin = request.POST.get('admin')
			pv = request.POST.get('pv')
			Billing_Config.objects.all().delete()
			Billing_Config.objects.create(
				admin_commission = admin,
				pv_percent = pv
			)
			messages.success(request, 'Billing Config Saved Successfully')
			return redirect('/admins/billing/config/')
		dic = {}
		if len(Billing_Config.objects.all()) > 0:
			dic = {'data':Billing_Config.objects.get()}
		return render(request, 'admin_app/billing-config.html', dic)
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_reject_product(request):
	if check_user_authentication(request, 'ADMIN'):
		reason = request.POST.get('reason')
		productvarinats=ProductVariants.objects.filter(id=request.POST.get('i')).first()
		proobj=Product.objects.filter(id=productvarinats.product.id).first()
		proobj.reasonforproductrejected=reason
		proobj.isproductrejected=True
		proobj.isactive=False
		productvarinats.isactive=False
		productvarinats.save()
		proobj.save()
		# user = Product.objects.get(id=request.POST.get('i')).store.vendor.user
		# notification(user, str('Product Rejected Beacause '+reason))
		return JsonResponse({'response':'Success'})
		#return redirect('/admins/productapproval')
	else:
		return redirect('/401/')



@csrf_exempt
def admin_update_product(request):
	if check_user_authentication(request, 'ADMIN'):
		product_name = request.GET.get('product_name')
		description = request.GET.get('description')
		Product.objects.filter(id=request.GET.get('i')).update(name=product_name,description=description)
		user = Product.objects.get(id=request.GET.get('i')).store.vendor.user
		notification(user,'Product Update by admin')
		return JsonResponse({'response':'Success'})
	else:
		return redirect('/401/')

def admin_tax_log(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'taxlog':TaxLog.objects.all().order_by('-id'),
			'orders':SalesOrder.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/taxlogs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_tds(request):
	if check_user_authentication(request, 'ADMIN'):
		if len(TDS.objects.all()) == 0 :
			TDS.objects.create(currenttds=0)
		
		tds =TDS.objects.filter().first()
		if request.method == 'POST':
			pay = request.POST.get('pay')
			if tds.currenttds >=  float(pay) and  float(pay) != 0 :
				
				TDSPay.objects.create(
					transactiondate = timezone.now(),
					currenttds = tds.currenttds,
					tdspaid = pay,
					tdsremaining = tds.currenttds - float(pay)
				)
				tds.currenttds = tds.currenttds - float(pay)
				tds.save()
				if tds.currenttds == 0:
					tdslogwallet=TDSLogWallet.objects.all()
					for x in tdslogwallet:
						if x.customer :
							TDSLogWalletTransaction.objects.create(tdslogwallet=x ,transactiondate = timezone.now(), transactiontype= 'Paid TDS : Rs.'+ str(x.currentbalance),amount=0, creditedamount=0 ,tdsamount=0,previousamount= round(x.currentbalance, 2),remainingamount=round(x.currentbalance,2) - round(x.currentbalance,2))
							TDSLogWallet.objects.filter(customer= x.customer).update(currentbalance = round(x.currentbalance, 2) - round(x.currentbalance, 2))

						if x.vendor :
							TDSLogWalletTransaction.objects.create(tdslogwallet=x ,transactiondate = timezone.now(), transactiontype= 'Paid TDS : Rs.'+ str(x.currentbalance),amount=0, creditedamount=0 ,tdsamount=0,previousamount= round(x.currentbalance, 2),remainingamount=round(x.currentbalance,2) - round(x.currentbalance,2))
							TDSLogWallet.objects.filter(vendor=x.vendor).update(currentbalance = round(x.currentbalance, 2) - round(x.currentbalance, 2))

						if x.admin :
							TDSLogWalletTransaction.objects.create(tdslogwallet=x ,transactiondate = timezone.now(),transactiontype= 'Paid TDS : Rs.'+ str(x.currentbalance),amount=0, creditedamount=0 ,tdsamount=0,previousamount= round(x.currentbalance, 2),remainingamount=round(x.currentbalance,2) - round(x.currentbalance,2))
							TDSLogWallet.objects.filter(admin=x.admin).update(currentbalance = round(x.currentbalance, 2) - round(x.currentbalance, 2))
       					
				messages.success(request, 'TDS has been paid sucessfully !')
				return redirect('/admins/total_tds')
			else:
				messages.warning(request, 'Insufficient balance !')
				return redirect('/admins/total_tds')
		dic = {'tds':tds, 'tds_transactions':TDSPay.objects.all(),'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),}
		return render(request, 'admin_app/total_tds.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_tds_withdraw(request):
	if check_user_authentication(request, 'ADMIN'):
		dic = {
			'tds_wallet':TDSLogWallet.objects.all(),'total_tds':TDS.objects.filter().first(), 
			'tds_wallet_transaction':TDSLogWalletTransaction.objects.all(),
			
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/tdslogs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_tds_log_details(request, id):
	if check_user_authentication(request, 'ADMIN'):

		tds_wallet=TDSLogWallet.objects.filter(id=id).first()
		tds_log = TDSLogWalletTransaction.objects.filter(tdslogwallet=id)
		dic = {

			'tds_wallet': tds_wallet,
			'tds_log': tds_log,
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		
		}
		return render(request, 'admin_app/tds_logs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def terms(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			title = request.POST.get('title')
			print(title, 'jkkkkkk')
			content = request.POST.get('content')
			print('content',content)
			termsandcondition.objects.all().delete()
			termsandcondition.objects.create(
				title=title,
				content=content
			)
		dic = {
			
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pages/terms-condition.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def privacy(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			title = request.POST.get('title')
			content = request.POST.get('content')
			privacypolicy.objects.all().delete()
			privacypolicy.objects.create(
				title=title,
				content=content
			)
		dic = {
		
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pages/privacy.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def contact(request):
	if check_user_authentication(request,'ADMIN'):
		if len(CompanyContactUs.objects.all()) == 0 :
			companycontactusobj=CompanyContactUs()
			companycontactusobj.updatedby= request.user
			companycontactusobj.save()
		dic = {
		    'data':CompanyContactUs.objects.filter().first(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		dic.update(get_cart_len(request))
		dic.update(get_wishlist_len(request))
		return render(request, 'admin_app/pages/contact.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def contact_update(request):
	if check_user_authentication(request,'ADMIN'):
		if len(CompanyContactUs.objects.all()) == 0 :
			companycontactusobj=CompanyContactUs()
			companycontactusobj.updatedby= request.user
			companycontactusobj.save()
   
		if request.method == 'POST':
			address= request.POST.get('address')
			mobile= request.POST.get('mobile')
			email= request.POST.get('email')
			whatsapp= request.POST.get('whatsapp')  
			facbook= request.POST.get('facbook')
			instagram= request.POST.get('instagram')
			twitter= request.POST.get('twitter')
			linkedin= request.POST.get('linkedin')
			
			
			companycontactusobj=CompanyContactUs.objects.filter().first()
			if address:
				companycontactusobj.address =address
			if mobile:			
				companycontactusobj.mobile = mobile
			if email:			
				companycontactusobj.email = email
			if whatsapp :
				companycontactusobj.whatsapp=whatsapp
			if facbook:			
				companycontactusobj.facbook = facbook
			if instagram:			
				companycontactusobj.instagram= instagram
			if twitter:			
				companycontactusobj.twitter = twitter
			if linkedin:			
				companycontactusobj.linkedin = linkedin
			companycontactusobj.updatedby= request.user
			companycontactusobj.save()
			messages.success(request,"Contact Deatils has been updated successfully !")
		
		return redirect('/admins/contact')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_about_us(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			# form = AboutForm(request.POST)
			title = request.POST.get('title')
			content = request.POST.get('content')
			print(content)
			image = request.FILES.get('file')
			print(image)
			AboutUs.objects.all().delete()
			AboutUs.objects.create(
				title=title,
				content=content,
				image=image,

			)
		dic = {
			'data':AboutUs.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pages/about-us.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_gallery(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			title = request.POST.get('title')
			image = request.FILES.getlist('pict')
			content = request.POST.get('description')
			print(content)
			for i in image:
				Gallery.objects.create(
					title=title,
					image=i,
					content=content
					)
				
		dic = {
			'data':Gallery.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pages/gallery.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_blog(request):
	if check_user_authentication(request,'ADMIN'):
		if request.method == 'POST':
			title = request.POST.get('title')
			content = request.POST.get('content')
			image = request.FILES.get('file')
			Blog.objects.all().delete()
			Blog.objects.create(
				title=title,
				content=content,
				image=image,

			)
		dic = {
			'data':Blog.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pages/blog.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_banner(request):
	if check_user_authentication(request,'ADMIN'):
		
		dic = {
			'data':HomeBanner.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/pages/banner.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_add_banner(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			category= request.POST.get('category')
			title= request.POST.get('title')
			description = request.POST.get('description')
			link = request.POST.get('link')
			image=request.FILES.get('image')
	
			if title:
				homebannerobj=HomeBanner.objects.create(title=title)			
				homebannerobj.updatedby=request.user
			if category:
				homebannerobj.category=ProductCategory.objects.filter(id=category).first()
	
			if description:
				homebannerobj.description=description
			if link:
				homebannerobj.link=link
			if image:
				homebannerobj.image=image
			if title:
				homebannerobj.save()
				return redirect("/admins/banner")
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_edit_banner(request,id):
	if check_user_authentication(request, 'ADMIN'):
		homebannerobj=HomeBanner.objects.filter(id=id).first()
		if request.method == 'POST':
			category= request.POST.get('category')
			title= request.POST.get('title')

			description = request.POST.get('description')
			link = request.POST.get('link')
			image=request.FILES.get('image')
			isactive= request.POST.get('isactive')
	
			if title:
				homebannerobj.title=title		
			if category:
				homebannerobj.category=ProductCategory.objects.filter(id=category).first()
		
			if description:
				homebannerobj.description=description
			if link:
				homebannerobj.link=link
			if image:
				homebannerobj.image=image
		

			    
			if isactive:
				print(isactive,type(isactive),'isactive')
				if isactive == 'on':
					isactive=True
				else:
					isactive=False
				homebannerobj.isactive=isactive
			else:
				isactive=False	
				homebannerobj.isactive=isactive
             
			homebannerobj.updatedby=request.user
			homebannerobj.save()
			return redirect("/admins/banner")
			
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_delete_banner(request,id):
	if check_user_authentication(request, 'ADMIN'):
		if id :
			homebannerobj=HomeBanner.objects.filter(id=id).first()
			homebannerobj.delete()
			return redirect("/admins/banner")
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_subscription_pack(request):
	if check_user_authentication(request, 'ADMIN'):
		if request.method == 'POST':
			one_month_subscription_charge = request.POST.get('one_month_subscription_charge')
			three_month_subscription_charge = request.POST.get('three_month_subscription_charge')
			six_month_subscription_charge = request.POST.get('six_month_subscription_charge')
			twelve_month_subscription_charge = request.POST.get('twelve_month_subscription_charge')
			pv_percentage = request.POST.get('pv_percentage')
			vendor_percentage =request.POST.get('vendor_percentage')
			SubscriptionCharge.objects.all().delete()
			SubscriptionCharge.objects.create(
			one_month_subscription_charge=one_month_subscription_charge,
			three_month_subscription_charge=three_month_subscription_charge,
			six_month_subscription_charge=six_month_subscription_charge,
			twelve_month_subscription_charge=twelve_month_subscription_charge,
			pv_percentage=pv_percentage,
			vendor_percentage=vendor_percentage)
			messages.success(request, 'Subscription Charges Updated Successfully')
			notification(request.user, 'Subscription Charges Changed.')
			return redirect('/admins/subscription-pack')
		dic = {'charge':SubscriptionCharge.objects.all(),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/subscription-charges.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def userSubscriptionRequest_admin(request):
	if request.user.role.level.level=='Admin':
		if request.method == 'GET':
			data = UserSubscriptionRequest.objects.all()
			dic={'data':data, 'categories':ProductCategory.objects.all(),}
			return render(request, 'admin_app/subscription-request.html', dic)


from django.contrib.auth.decorators import login_required
import random
from django.db import transaction
import datetime


login_required('/')
@csrf_exempt
def adminbalanacetransfer(request):
	print(request.user.email,'OTPPP')
	bal = Wallet.objects.get(admin=request.user).currentbalance
	
	vandordata = Vendor.objects.filter(verified = True)
	transectiondata = WalletBalanceTransfer.objects.filter(sender=request.user.username).order_by('-id')
	context = {
			'vendordata': vandordata,'customerlist':Customer.objects.filter(isactive=True),
			'transectiodetails':transectiondata,
			'bal':bal,
			# 'notification':get_notifications(request.user,'ADMIN'),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False))
		}

	

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
		# notification(request.user, 'OTP sent successfully.')
		messages.success(request, 'OTP sent successfully.')
		return render(request,'admin_app/otpverify.html')
	return render(request,'admin_app/customerwallettransfer.html',context=context)
# else :
# 	messages.error(request,'Payments Mode off')
# 	return render(request,'admin_app/customerwallettransfer.html',context=context)


login_required('/')
@transaction.atomic
def transfer_amount_admin(request):
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
		print(senderotp)
		# reciverotp = int(request.POST.get('otp2') )
		# print(datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f'))

		# if datetime.datetime.now() < datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f') :
		
			# if senderotp == request.session['senderotp'] and reciverotp == request.session['reciverotp']:
		if senderotp == request.session['senderotp']:
			print('hjhjjjjjjjjjjjj')
			if Wallet.objects.get(admin=request.user).currentbalance >= request.session['amount']:
				print('LLLLLLLLLLLLLLLLLLL')
               
				make_wallet_transaction("ADMIN",request.user, request.session['amount'],'DEBIT')
				reciveruser=User.objects.get(username = request.session['recivername'])
				if reciveruser.groups.filter(name="ADMIN"):
					group_name="ADMIN"   
				elif reciveruser.groups.filter(name="VENDOR"):
					group_name="VENDOR"  
				elif reciveruser.groups.filter(name="CUSTOMER"):
						group_name="CUSTOMER"  
				make_wallet_transaction(group_name,User.objects.get(username = request.session['recivername']), 
					request.session['amount'],'CREDIT')
				print(request.session['recivername'])
				transfer_into_another_account(request.user, request.user.username,
					request.session['recivername'], request.session['amount'])
				print('done')
				messages.success(request,'Successfully Transfered')
			
				return redirect('balanacetransfers')


			else :
				messages.error(request,'Not having sufficient balance')
				return redirect('balanacetransfers')

		else :
			messages.error(request,'OTP is not Correct')
			return redirect('otpvalidations')
		# else:
		# 	messages.error(request,'Timeout')
		# 	return redirect('balanacetransfer')
	# return redirect('balanacetransfers')
	return render(request,'admin_app/otpverify.html')




from .forms import *

@csrf_exempt
def staff_list(request):
	if check_user_authentication(request, 'ADMIN'):
		form = StaffCreationForm()
		form1 = Staffs_User_Form()
		if request.method == 'POST':
			form = StaffCreationForm(request.POST)
			form1 = Staffs_User_Form(request.POST,request.FILES)
			print(form1)

			if form.is_valid() and form1.is_valid() :

				first_name = form.cleaned_data.get('first_name')
				last_name = form.cleaned_data.get('last_name') 
				email = form.cleaned_data.get('email')
				password = form.cleaned_data.get('password') 
				
				phone = form1.cleaned_data.get('phone') 
				address = form1.cleaned_data.get('address')
				zipcode = form1.cleaned_data.get('zipcode') 
				gender = form1.cleaned_data.get('gender')
				profile_pic = form1.cleaned_data.get('profile_pic') 
				deparment = form1.cleaned_data.get('deparment')
				designation = form1.cleaned_data.get('designation') 

				print(phone,'SSSSSSSSSS')
				user = User.objects.create_user(username= email,first_name = first_name,last_name=last_name,
				 email= email,password=password,is_staff=True,isactive= True)   

				print(user,'UUUUUUUUUUUUU')
				print(address,'AAAAAAAAa')

				levelss=Levels.objects.filter(level='Staff').first()

				Role.objects.create(user=user,level=levelss)

				staff= Staffs_User.objects.create(user= user,phone = phone,address=address,
				 zipcode= zipcode,gender=gender,profile_pic=profile_pic,  deparment=deparment,designation=designation) 
			
				message = ('%(email)s is added as a staff.') % {'email': email} 
				messages.success(request, message)
				return redirect('/admins/staff_list')
    
		dic = {
			'categories':ProductCategory.objects.all(),'form':form,'form1':form1,
			'data':Staffs_User.objects.all(),
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
		}
		return render(request, 'admin_app/staffs_list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_activate_isactive_staff(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		staff=Staffs_User.objects.filter(id=id_).first()
		user = User.objects.filter(id=staff.user.id).update(isactive=True)
		sub = 'AVPL -Staff account activated Successfully'
		msg = '''Hi there!
Your AVPL Staff account activated Successfully, you can login.

Thanks!'''
		EmailMessage(sub,msg,to=[staff.user.email]).send()
		messages.success(request, 'AVPL Staff account activated Successfully !!!!')
		return redirect('/admins/staff_list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def admin_deactivate_isactive_staff(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		staff=Staffs_User.objects.filter(id=id_).first()
		user = User.objects.filter(id=staff.user.id).update(isactive=False)
		sub = 'AVPL -AVPL Staff account Deactivate Successfully'
		msg = '''Hi there!
Your AVPL Staff account Deactivate Successfully.

Thanks!'''
		EmailMessage(sub,msg,to=[staff.user.email]).send()
		messages.success(request, 'AVPL Staff account Deactivate Successfully !!!!')
		return redirect('/admins/staff_list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_staff_profile(request):
	if check_user_authentication(request, 'ADMIN'):
		staff = Staffs_User.objects.get(id=request.GET.get('i'))
		user = User.objects.get(id=staff.user.id)
		updateform = Users_Form( instance=user)
		updateform2  = Staffs_User_Form(instance=staff)
		if request.method == 'POST':

			updateform = Users_Form(request.POST,request.FILES, instance=user)
		
			if updateform.is_valid():
				updateform.save()

			updateform2 = Staffs_User_Form(request.POST,request.FILES, instance=staff)
		
			if updateform2.is_valid():
				updateform2.save()
		
		dic = {
			'user':user,'staff':staff,'updateform':updateform,'updateform2':updateform2,
			'notification':get_notifications(request.user,'ADMIN'),
			'notification_len':len(Notification.objects.filter(admin=request.user, isread=False)),
			'data':Staffs_User.objects.all(),
			'categories':ProductCategory.objects.all()
		}

		return render(request, 'admin_app/staff-profile.html', dic)
	else:
		return HttpResponse('Error 500 : Unauthorized User')

@csrf_exempt
def admin_staff_delete(request):
	if check_user_authentication(request, 'ADMIN'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		staff=Staffs_User.objects.filter(id=id_).first()
		user = User.objects.filter(id=staff.user.id).delete()
		print(staff,'SSSSSSSSsss')
		staff.delete()
		messages.success(request, 'AVPL Staff account Deleted Successfully !!!!')
		return redirect('/admins/staff_list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

