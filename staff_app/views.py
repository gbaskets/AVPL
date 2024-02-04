from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators import csrf
from admin_app.models import *
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
from staff_app.utils import *
from django.utils import timezone
import base64
from django.core.files.base import ContentFile
@csrf_exempt
def staff_show(request):
#	for x in ProductCategory.objects.all():
#		PointValue.objects.create(category=x)
#	ProductCategory.objects.filter(name='Computers').delete()
#	User.objects.create_user(email='staff@avpl.com',username='staffavpl',password='1234')
#	user = User.objects.get(email='staff@avpl.com')
#	Role(user=user, level=Levels.objects.get(level='Staff')).save()
	return HttpResponse('Done!')

@csrf_exempt
def staff_login(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		if User.objects.filter(email=email).exists():
			chk_user = User.objects.get(email=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if check_user_authentication(request, 'Staff'):
					return redirect('/staffs/dashboard')
				else:
					messages.info(request, 'You are not allowed to login')
					logout(request)
					return redirect('/staffs/')
			else:
				messages.info(request,'Incorrect Staff Password')
				return redirect('/staffs/')
		elif User.objects.filter(username=email).exists():
			chk_user = User.objects.get(username=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if check_user_authentication(request, 'Staff'):
					return redirect('/staffs/dashboard')
				else:
					messages.info(request, 'You are not allowed to login')
					logout(request)
					return redirect('/staffs/')
			else:
				messages.info(request,'Incorrect Staff Password')
				return redirect('/staffs/')
		else:
			messages.info(request,'Incorrect Staff Email/Username')
			return redirect('/staffs/')
	else:
		if request.user.is_authenticated and check_user_authentication(request, 'Staff'):
			return redirect('/staffs/dashboard')
		else:
			return render(request, 'staff_app/login.html', {})
@csrf_exempt
def staff_dashboard(request):
	if check_user_authentication(request, 'Staff'):
		pv = 0.0
		# pv_year = 0.0
		d = datetime.datetime.now()
		if len(Yearly_PV.objects.all()) == 0:
			Yearly_PV.objects.create()
		for pv_trn in PVTransactions.objects.all():
			if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
				pv += pv_trn.pv
		if Current_PV.objects.all() == None:
			Current_PV.objects.create(pv = pv)
			
		# # for pv_trn in PVTransactions.objects.all():
		# # 	if pv_trn.transaction_date.strftime("%Y") == d.strftime("%Y"):
		# # 		pv_year += pv_trn.pv
		# # Yearly_PV.objects.update(pv = pv_year)
		# # print(pv_year<pv)
		# pv = round(pv,2)
		# user=request.user
		# user_permissions = user.user_permissions.all()
    
		for perm in request.user.user_permissions.all():
			print(perm.codename)


		# permissions = Permission.objects.filter(Q(codename='can_create_product') | Q(codename='can_view_product'))

		# print(user_permissions,'PPPPPPPPPp')

		dic = {
			'categories':ProductCategory.objects.all(),
			'commission':Commission.objects.all(),
			'savings':Savings.objects.all(),
			'wallet':Wallet.objects.all(),
			'transactions':CommissionTransaction.objects.all().order_by('-id'),
			'total_pv':Current_PV.objects.all().order_by('-id').first,
			'year_pv':Yearly_PV.objects.all(),
			'wallettransactions':WalletTransaction.objects.all().order_by('-id'),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/dashboard.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_send_money(request):
	if check_user_authentication(request, 'Staff'):
		send_profit_to_users()
		return redirect('/staffs/dashboard')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_product_categories(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			name = request.POST.get('name')
			tax = request.POST.get('tax')
			commission = request.POST.get('commission')
			image = request.FILES['image']
			if ProductCategory.objects.filter(name=name).exists():
				messages.info(request, 'Product Category Already Exists')
				return redirect('/staffs/productcategories')
			else:
				ProductCategory.objects.create(name=name, tax=tax, image=image, commission=commission)
				PointValue.objects.create(category=ProductCategory.objects.get(name=name))
				messages.info(request, 'Product Category Added Successfully !!!!')
				return redirect('/staffs/productcategories')
		else:
			dic = {
				'data':ProductCategory.objects.all(),
				'categories':ProductCategory.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'staff_app/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_edit_product_category(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			print('IIIIIIIIIIIIII', id_)
			dic = {
				'data' : ProductCategory.objects.filter(id=id_),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'staff_app/edit-product-category.html', dic)
		if request.method == 'POST':
			id_ = request.GET.get('id_')
			print(id_)
			data = ProductCategory.objects.filter(id=id_).first()
			print(data)
			name = request.POST.get('name')
			tax = request.POST.get('tax')
			commission = request.POST.get('commission')
			print('KKKKKKKKKKKKKKKK',name, tax)
			image = request.FILES.get('image')
			if name and tax is None and commission is None and image is None:
				data.name = name
				data.save()
			if tax and name is None and commission is None and image is None:
				data.tax = tax
			if commission and tax is None and name is None and image is None:
				data.commission = commission
				data.save()
			if image and tax is None and commission is None and name is None:
				data.image = image
				data.save()
			else:
				data.name = name
				data.tax = tax
				data.commission = commission
				data.image = image
				data.save()
			dic = {
			# 'data' : data,
			'data':ProductCategory.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			messages.info(request, 'Product Category Edited Successfully !!!!')
			return redirect('/staffs/productcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_delete_product_category(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			ProductCategory.objects.filter(id=id_).delete()
			messages.info(request, 'Product Category Deleted Successfully !!!!')
			return redirect('/staffs/productcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_product_sub_categories(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			name = request.POST.get('name')
			image = request.FILES['image']
			category = request.POST.get('category')
			if ProductSubCategory.objects.filter(name=name).exists():
				messages.info(request, 'Product Sub Category Already Exists')
				return redirect('/staffs/productsubcategories')
			else:
				ProductSubCategory.objects.create(category=ProductCategory.objects.get(id=category),name=name, image=image)
				messages.info(request, 'Product Sub Category Added Successfully !!!!')
				return redirect('/staffs/productsubcategories')
		else:
			dic = {
				'categories':ProductCategory.objects.all(),
				'data':ProductSubCategory.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'staff_app/product-sub-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_edit_product_sub_categories(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			print('IIIIIIIIIIIIII', id_)
			dic = {
				'categories':ProductCategory.objects.all(),
				'data': ProductSubCategory.objects.filter(id=id_),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'staff_app/edit-product-sub-category.html', dic)
			
		if request.method == 'POST':
			id_ = request.GET.get('id_')
			print(id_)
			data = ProductSubCategory.objects.filter(id=id_).first()
			print(data)
			name = request.POST.get('name')
			category = request.POST.get('category')
			print('KKKKKKKKKKKKKKKK',name, category)
			image = request.FILES.get('image')
			data.name = name
			data.category=ProductCategory.objects.get(id=category)
			data.image = image
			data.save()

			dic = {
			# 'data' : data,
			'data':ProductSubCategory.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			messages.info(request, 'Product Sub-Category Edited Successfully !!!!')
			return redirect('/staffs/productsubcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_delete_product_sub_category(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			ProductSubCategory.objects.filter(id=id_).delete()
			messages.info(request, 'Product Sub Category Deleted Successfully !!!!')
			return redirect('/staffs/productsubcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_product_sub_sub_categories(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			name = request.POST.get('name')
			image = request.FILES['image']
			subcategory = request.POST.get('subcategory')
			if ProductSubSubCategory.objects.filter(name=name).exists():
				messages.info(request, 'Product Sub Sub Category Already Exists')
				return redirect('/staffs/productsubsubcategories')
			else:
				ProductSubSubCategory.objects.create(subcategory=ProductSubCategory.objects.get(id=subcategory),name=name, image=image)
				messages.info(request, 'Product Sub Sub Category Added Successfully !!!!')
				return redirect('/staffs/productsubsubcategories')
		else:
			dic = {
				'categories':ProductCategory.objects.all(),
				'subcategories':ProductSubCategory.objects.all(),
				'data':ProductSubSubCategory.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'staff_app/product-sub-sub-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_edit_product_sub_sub_categories(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			print('IIIIIIIIIIIIII', id_)
			dic = {
				'categories':ProductCategory.objects.all(),
				'subcategories':ProductSubCategory.objects.all(),
				'data':ProductSubSubCategory.objects.filter(id=id_),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'staff_app/edit-product-sub-sub-category.html', dic)
			
		if request.method == 'POST':
			id_ = request.GET.get('id_')
			print(id_)
			data = ProductSubSubCategory.objects.filter(id=id_).first()
			print(data)
			name = request.POST.get('name')
			subcategory = request.POST.get('subcategory')
			
			image = request.FILES.get('image')
			data.name = name
			data.subcategory=ProductSubCategory.objects.get(id=subcategory)
			data.image = image
			data.save()

			dic = {
			# 'data' : data,
		        'categories':ProductCategory.objects.all(),
				'subcategories':ProductSubCategory.objects.all(),
				'data':ProductSubSubCategory.objects.filter(id=id_),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			messages.info(request, 'Product Sub-Sub-Category Edited Successfully !!!!')
			return redirect('/staffs/productsubsubcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_delete_product_sub_sub_category(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			ProductSubSubCategory.objects.filter(id=id_).delete()
			messages.info(request, 'Product Sub Sub Category Deleted Successfully !!!!')
			return redirect('/staffs/productsubsubcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_kyc_requests(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'data':Vendor.objects.filter(doc_submitted=True, is_active=False),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/kyc-requests.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

# def staff_kyc_vendors(request):
# 	if check_user_authentication(request, 'Staff'):
# 		dic = {
# 			'categories':ProductCategory.objects.all(),
# 			'data':Vendor.objects.filter(doc_submitted=True, is_active=True),
# 			'notification':get_notifications(request.user),
# 			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
# 		}
# 		return render(request, 'staff_app/kyc-vendors.html', dic)
# 	else:
# 		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_vendor_list(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'data':Vendor.objects.filter(doc_submitted=True, is_active=True),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/vendor_list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_is_activate_approved_avpl_vendor(request):
	if check_user_authentication(request, 'Staff'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(is_AVPL_Vendor=True)
		sub = 'AVPL -AVPL Vendor Approved Successfully'
		msg = '''Hi there!
Your AVPL Vendor Approved Successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Approved Successfully !!!!')
		notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		notification(vendor.user, 'AVPL Vendor Approved Successfully.')
		return redirect('/staffs/vendor-list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_is_deactivate_approved_avpl_vendor(request):
	if check_user_authentication(request, 'Staff'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(is_AVPL_Vendor=False)
		sub = 'AVPL -AVPL Vendor Deactivate Successfully'
		msg = '''Hi there!
Your AVPL Vendor Deactivate Successfully.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Deactivate Successfully !!!!')
		notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		notification(vendor.user, 'AVPL Vendor Deactivate Successfully.')
		return redirect('/staffs/vendor-list')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_vendor_profile(request):
	if check_user_authentication(request, 'Staff'):
		vendor = Vendor.objects.get(id=request.GET.get('i'))
		vendoc = VendorDocs.objects.get(vendor__user=vendor.user)
		store = Store.objects.get(vendor=vendor)
		images = StoreImages.objects.get(store=store)
		vanadd = Vendor.objects.get(user=vendor.user)
		dic = {
			'vendoc':vendoc,
			'store':store,
			'info':vanadd,
			'vendor':vendor,
			'images':images,
			'categories':ProductCategory.objects.all()
		}
		return render(request,'staff_app/vendor-profile.html', dic)
	else:
		return HttpResponse('Error 500 : Unauthorized User')
@csrf_exempt
def staff_activate_vendor(request):
	if check_user_authentication(request, 'Staff'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(is_active=True)
		sub = 'AVPL - Vendor Account Activated Successfully'
		msg = '''Hi there!
Your AVPL Vendor Account has been activated successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'Vendor Activated Successfully !!!!')
		notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		notification(vendor.user, 'Profile Activated Successfully.')
		return redirect('/staffs/kycrequests')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_activate_approved_avpl_vendor(request):
	if check_user_authentication(request, 'Staff'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(is_AVPL_Vendor=True)
		sub = 'AVPL -AVPL Vendor Approved Successfully'
		msg = '''Hi there!
Your AVPL Vendor Approved Successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'AVPL Vendor Approved Successfully !!!!')
		notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		notification(vendor.user, 'AVPL Vendor Approved Successfully.')
		return redirect('/staffs/kycrequests')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_pv_wallet(request):
	if check_user_authentication(request, 'Staff'):
		print(request.user)
		dic = {'user':UserData.objects.get(user=request.user),
			'pv':fetch_pv(request.user),
			'transactions':fetch_pv_transactions(request.user),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/pv.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def staff_point_value(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			c=request.GET.get('c')
			category = ProductCategory.objects.get(id =c )
			dic = {'categories':ProductCategory.objects.all(), 'point':PointValue.objects.get(category=category)}
			return render(request,'staff_app/point-value.html', dic)
		elif request.method == 'POST':
			new = request.POST.get('new')
			id_ = request.POST.get('category')
			category = ProductCategory.objects.get(id = id_)
			PointValue.objects.filter(category=category).update(percentage=new)
			messages.success(request, 'Point Value Percentage Updated Successfully !!!!')
			notification(request.user, 'PV of '+category.name+' set to '+ str(PointValue.objects.get(category=category).percentage))
			return redirect('/staffs/point/?c='+id_)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_create_link(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/create-link.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def wallet_details(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'wallet':Wallet.objects.filter(user__is_superuser=True),'categories':ProductCategory.objects.all(),
			'wallettransactions':WalletTransaction.objects.filter(wallet__user__is_superuser=True),
			# 'wallettransactions':WalletTransaction.objects.all(),
		}
		return render(request, 'staff_app/wallet.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_generate_link_left(request):
	if check_user_authentication(request, 'Staff'):
		data = {'link':generate_link(request.user, 'Staff','left')}
		# messages.success(request, 'You have been generated left link !')
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})
@csrf_exempt
def staff_generate_link_right(request):
	if check_user_authentication(request, 'Staff'):
		data = {'link':generate_link(request.user, 'Staff','right')}
		# messages.success(request, 'You have been generated right link !')
		return JsonResponse(data)
		
	else:
		return JsonResponse({'response':'Error'})

@csrf_exempt
def staff_under_trees(request):
	if check_user_authentication(request, 'Staff'):
		print(request.user)
		
        
		for users in MLMStaff.objects.all():
			child=users.child
			print(fetch_user_tree(child),'TTTTTTTTTTt')

		dic = {'data':MLMStaff.objects.all(), 'categories':ProductCategory.objects.all(),
		'tree':fetch_user_tree(child),
		'notification':get_notifications(request.user),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/under-trees.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def staff_under_trees_level(request):
	if check_user_authentication(request, 'Staff'):
		referal_obj = Level_Plan_Referrals.objects.filter(referrals__id=request.user.id).first()
		referals = Level_Plan_Referrals.objects.filter(level_plan_referral=referal_obj)
		dic = {'data':referals, 'categories':ProductCategory.objects.all(),}
		return render(request, 'staff_app/under-trees-level.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def genealogyTree_binary(request):
	if check_user_authentication(request, 'Staff'):

		for users in MLMStaff.objects.all():
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
						'notification':get_notifications(request.user),
						'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
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
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
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
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
						}
			return render(request, 'staff_app/genealogyTree_binary.html',dic)
		if node_V.left  is not None:	
			return render(request, 'staff_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv,'usrpvl':usrpvl,'nodel':nodel,
						'noder':noder,})
		
		if node_V.right is not None:					
		    return render(request, 'staff_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv,'usrpvr':usrpvr,
						})
		else:
			print('None')
			return render(request, 'staff_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv})
	else:
		return render(request, '403.html')

@csrf_exempt
def genealogyTree_level(request):
	if check_user_authentication(request, 'Staff'):
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
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				'referals_user':referals_user,
				
			}
			return render(request, 'staff_app/genealogyTree_level.html',dic)
			
			
		if referal_obj or referalss  is not None:	
			
		
			dic = {
				# 'user':UserData.objects.get(user=request.user),
				'referals':referals,
				# 'sponser_r':referal_obj.referrals,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}

		
		else:
			print('none')
			dic = {
				# 'user':UserData.objects.get(user=request.user),
				'referals':referals,'usrpvs':usrpvs,
				# 'sponser_r':referal_obj,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
		return render(request, 'staff_app/genealogyTree_level.html',dic)
	else:
		return render(request, '403.html')















@csrf_exempt
def staff_delivery_charges(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			charge = request.POST.get('charge')
			DeliveryCharge.objects.all().delete()
			DeliveryCharge.objects.create(amount=charge)
			messages.success(request, 'Charges Updated Successfully')
			notification(request.user, 'Delivery Charges Changed.')
			return redirect('/staffs/deliverycharges')
		dic = {'charge':DeliveryCharge.objects.all(),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/delivery-charges.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_payment_info(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'orders':Orders.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/payment-info.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_orders(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'orders':OrderItems.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_pvpairvalue(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			new = request.POST.get('new')
			PVPairValue.objects.all().delete()
			PVPairValue.objects.create(pair_value=new)
			notification(request.user, 'PV Pair Value Changed')
			return redirect('/staffs/setpvpair')
		dic = {'data':PVPairValue.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/set-pv-pair.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_withdraw(request):
	if check_user_authentication(request, 'Staff'):
		dic = {'users':UserWithdrawRequest.objects.all(), 'vendors':VendorWithdrawRequest.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/withdraw.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_change_withdraw_status(request):
	if check_user_authentication(request, 'Staff'):
		type_ = request.GET.get('t')
		id_ = request.GET.get('i')
		status = request.GET.get('s')
		if type_ == 'u':
			UserWithdrawRequest.objects.filter(id=id_).update(is_active=status)
			withdraw = UserWithdrawRequest.objects.get(id=id_)
			if status == '2':
				TDS_Log.objects.create(user=withdraw.user,amount=withdraw.amount, tds_amt=withdraw.tds)
				make_wallet_transaction(withdraw.user, (withdraw.amount+withdraw.tds), 'DEBIT')
				notification(withdraw.user, 'Rs'+str(withdraw.amount)+' debited from your wallet.')
			notification(withdraw.user, 'Withdraw Request Status Changed.')
		elif type_ == 'v':
			VendorWithdrawRequest.objects.filter(id=id_).update(is_active=status)
			withdraw = VendorWithdrawRequest.objects.get(id=id_)
			if status == '2':
				make_wallet_transaction(withdraw.user, withdraw.amount, 'DEBIT')
				notification(withdraw.user, 'Rs'+str(withdraw.amount)+' debited from your wallet.')
			notification(withdraw.user, 'Withdraw Request Status Changed.')
		messages.success(request, 'Status Changed Successfully')
		return redirect('/staffs/withdraw')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_query(request):
	if check_user_authentication(request, 'Staff'):
		dic = {'queries':Query.objects.all().order_by('-id'),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/query.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_query_result(request):
	if check_user_authentication(request, 'Staff'):
		dic = {'query':Query.objects.get(id=request.GET.get('query_id')),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/query-result.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_change_query_status(request):
	if check_user_authentication(request, 'Staff'):
		Query.objects.filter(id=request.GET.get('query')).update(status=request.GET.get('status'))
		user = Query.objects.get(id=request.GET.get('query')).user
		notification(user, 'Query Status Changed.')
		return JsonResponse({'response`	':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_query_send_reply(request):
	if check_user_authentication(request, 'Staff'):
		if request.method =="POST":
			img_data=request.POST.get('image')
			format, imgstr = img_data.split(';base64,')
			ext = format.split('/')[-1]
			image_data = ContentFile(base64.b64decode(imgstr), name='reply_image.'+ext)
			
			q_data=Query.objects.get(id=request.POST.get('query'))
			q_data.reply=request.POST.get('reply')
			q_data.reply_image=image_data
			q_data.save()
			
			# update(
			# 	reply=request.POST.get('reply'),reply_image=image_data
			# )
			query = Query.objects.get(id=request.POST.get('query'))
			if query.anonymous:
				msg = '''Hi '''+query.name+''',

	'''+query.reply+''' ,
	'''+query.reply_image+'''

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
def staff_set_pv_conversion(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			value = request.POST.get('new')
			PVConversionValue.objects.all().delete()
			PVConversionValue.objects.create(
				conversion_value = value
			)
			notification(request.user, 'User Share Percent Changed.')
			return redirect('/staffs/setpvconversion')
		dic = {'data':PVConversionValue.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/set-pv-conversion.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_direct_referal(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			value = request.POST.get('value')
			DirectReferalCommission.objects.all().delete()
			DirectReferalCommission.objects.create(
				percentage=value,
			)
			notification(request.user,'Direct Referal Commission Precent Changed.')
			return redirect('/staffs/direct-referal')
		dic = {'data':DirectReferalCommission.objects.all(),
		'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/direct-referal.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def staff_leadership_bonus_set(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			value = request.POST.get('leader')
			target = request.POST.get('target')
			UserLeadershipBonusCommission.objects.all().delete()
			UserLeadershipBonusCommission.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/staffs/leadershipbonus')
		dic = {'data':UserLeadershipBonusCommission.objects.all(),
		'notification':get_notifications(request.user),
		'leadership_bonus':get_leadership_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/leadership-bonus.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_travel_fund_set(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			TravelFund.objects.all().delete()
			TravelFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/staffs/travelfund')
		dic = {'data':TravelFund.objects.all(),
		'notification':get_notifications(request.user),
		'travel_fund':get_travel_fund_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/travel-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_car_fund_set(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			CarFund.objects.all().delete()
			CarFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/staffs/carfund')
		dic = {'data':CarFund.objects.all(),
		'notification':get_notifications(request.user),
		'car_fund':get_car_fund_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/car-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_house_fund_set(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			HouseFund.objects.all().delete()
			HouseFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/staffs/housefund')
		dic = {'data':HouseFund.objects.all(),
		'notification':get_notifications(request.user),
		'house_fund':get_house_fund_eligible_users(request),'categories':ProductCategory.objects.all(),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/house-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_directorship_fund_set(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			DirectorshipFund.objects.all().delete()
			DirectorshipFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/staffs/directorshipfund')
		dic = {'data':DirectorshipFund.objects.all(),
		'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
		'directorship_fund':get_directorship_fund_eligible_users(request),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/directorship-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def staff_product(request):
	if check_user_authentication(request, 'Staff'):
		product = Product.objects.get(id=request.GET.get('id'))
		dic = {
			'product':product,
			'images':ProductImages.objects.filter(product=product),
			'variants':ProductVariant.objects.filter(product=product),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request,'staff_app/product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_product_approval(request):
	if check_user_authentication(request, 'Staff'):
		dic = {'data':Product.objects.filter(is_active=False, product_rejection=False),
			'rejected_product':Product.objects.filter(is_active=False, product_rejection=True),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/product-approval.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_product_list(request):
	if check_user_authentication(request, 'Staff'):
		
		dic = {
			'products':Product.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/product_list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_product_basic_edit(request):
	if check_user_authentication(request, 'Staff'):
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
				# is_active= False
			)
			messages.success(request, 'Product Updated Successfully')
			return redirect('/staffs/product?id='+request.POST.get('id'))
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_delete_product_image(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			ProductImages.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_delete_product_variant(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			ProductVariant.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_product_out_of_stock(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'GET':
			Product.objects.filter(id=request.GET.get('i')).update(stock=0)
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_activate_product(request):
	if check_user_authentication(request, 'Staff'):
		Product.objects.filter(id=request.GET.get('p')).update(is_active=True)
		user = Product.objects.get(id=request.GET.get('p')).store.vendor.user
		notification(user, 'Product Activated Successfully.')
		return redirect('/staffs/productapproval')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_taxation(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			pay = request.POST.get('pay')
			TaxPay.objects.create(
				transaction_date = timezone.now(),
				tax_current = Tax.objects.all()[0].current_tax,
				tax_paid = pay,
				tax_remaining = (Tax.objects.all()[0].current_tax - float(pay))
			)
			Tax.objects.all().update(current_tax = (Tax.objects.all()[0].current_tax - float(pay)))
			return redirect('/staffs/tax')
		dic = {'tax':Tax.objects.all(), 'transactions':TaxPay.objects.all()}
		return render(request, 'staff_app/tax.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

# def staff_users(request):
# 	if check_user_authentication(request, 'Staff'):
# 		print("printing here Users PV")
# 		pv=UserPV.objects.all()
# 		print(pv)
# 		dic = {'users':User.objects.all(),'pv':pv}
# 		return render(request, 'staff_app/users.html', dic)
# 	else:
# 		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_users(request):
	if check_user_authentication(request, 'Staff'):
		users = User.objects.filter(is_active=True)
		lt = []
		for x in users :
			print(x,'USSSSSSSSs')
			roles=Role.objects.filter(user=x).first()

			print(roles,'RRRRRRR')
			if x.role.level.level == 'User':
				dic = {'user':x}
				dic.update(get_user_indecater(x))
				lt.append(dic)
			elif x.role.level.level == 'Vendor':
			    lt.append({'user':x})
		print(lt,'List')
		
		return render(request, 'staff_app/users.html',{'users':lt})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_users_delete(request):
	if check_user_authentication(request, 'Staff'):
		User.objects.filter(id=request.GET.get('i')).delete()
		messages.success(request, 'User Deleted Successfully')
		return redirect('/staffs/users')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def user_vendor_commission(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			new = request.POST.get('new')
			UserVendorCommission.objects.all().delete()
			UserVendorCommission.objects.create(percentage=new)
			notification(request.user, 'User Vendor Commission Changed')
			return redirect('/staffs/uservendorcommission')
		dic = {'data':UserVendorCommission.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/set-user-vendor-commission.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_level_settings(request):
	if check_user_authentication(request, 'Staff'):
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
			return redirect('/staffs/settings/')
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
		return render(request, 'staff_app/level.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_fetch_groups(request):
	if check_user_authentication(request, 'Staff'):
		levels = Level_Settings.objects.all()
		dic = {}
		if len(levels) > 0:
			dic = {'level':levels[0], 'groups':Level_Group.objects.filter(level=levels[0]),'categories':ProductCategory.objects.all(),}
		return render(request, 'staff_app/level-table.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_edit_group(request):
	if check_user_authentication(request, 'Staff'):
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
def staff_level_settings_level_plan(request):
	if check_user_authentication(request, 'Staff'):
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
			return redirect('/staffs/level/settings/')
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
		return render(request, 'staff_app/level-level_plan.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_fetch_groups_level(request):
	if check_user_authentication(request, 'Staff'):
		levels = Level_Settings_Level_Plan.objects.all()
		dic = {}
		if len(levels) > 0:
			dic = {'level':levels[0], 'groups':Level_Group_Level_Plan.objects.filter(level=levels[0]),'categories':ProductCategory.objects.all(),}
		return render(request, 'staff_app/level-table.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_edit_group_level(request):
	if check_user_authentication(request, 'Staff'):
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
def staff_min_cart_value(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			Min_Amount_For_Free_Delivery.objects.all().delete()
			Min_Amount_For_Free_Delivery.objects.create(amount=amount)
			return redirect('/staffs/minmumcartvalue/')
		dic = {'cart':Min_Amount_For_Free_Delivery.objects.get()}
		return render(request, 'staff_app/set-min-cart-value.html', dic)
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_billing_config(request):
	if check_user_authentication(request, 'Staff'):
		if request.method == 'POST':
			staff = request.POST.get('staff')
			pv = request.POST.get('pv')
			Billing_Config.objects.all().delete()
			Billing_Config.objects.create(
				staff_commission = staff,
				pv_percent = pv
			)
			messages.success(request, 'Billing Config Saved Successfully')
			return redirect('/staffs/billing/config/')
		dic = {}
		if len(Billing_Config.objects.all()) > 0:
			dic = {'data':Billing_Config.objects.get()}
		return render(request, 'staff_app/billing-config.html', dic)
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_reject_product(request):
	if check_user_authentication(request, 'Staff'):
		reason = request.POST.get('reason')
		Product.objects.filter(id=request.POST.get('i')).update(product_reject_reason=reason,product_rejection=True,is_active=False)
		user = Product.objects.get(id=request.POST.get('i')).store.vendor.user
		notification(user, str('Product Rejected Beacause '+reason))
		return JsonResponse({'response':'Success'})
		#return redirect('/staffs/productapproval')
	else:
		return redirect('/401/')

@csrf_exempt
def staff_update_product(request):
	if check_user_authentication(request, 'Staff'):
		product_name = request.GET.get('product_name')
		description = request.GET.get('description')
		Product.objects.filter(id=request.GET.get('i')).update(name=product_name,description=description)
		user = Product.objects.get(id=request.GET.get('i')).store.vendor.user
		notification(user,'Product Update by staff')
		return JsonResponse({'response':'Success'})
	else:
		return redirect('/401/')
@csrf_exempt
def staff_gst_log(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'order':GST_Log.objects.all().order_by('-id'),
			'orders':OrderItems.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/gstlogs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_tds_withdraw(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'tds_log':TDS_Log.objects.all(),
			'users':UserWithdrawRequest.objects.all(),
			'vendors':VendorWithdrawRequest.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/tdslogs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def terms(request):
	if check_user_authentication(request,'Staff'):
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
			'data':termsandcondition.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/terms-condition.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def privacy(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			title = request.POST.get('title')
			content = request.POST.get('content')
			privacypolicy.objects.all().delete()
			privacypolicy.objects.create(
				title=title,
				content=content
			)
		dic = {
			'data':privacypolicy.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/privacy.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def contact(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			address= request.POST.get('address')
			contact_no= request.POST.get('phone')
			gmail_id= request.POST.get('gmail')
			facbook_id= request.POST.get('fb')
			instagram_id= request.POST.get('insta')
			twitter_id= request.POST.get('twitter')
			linkedin_id= request.POST.get('linkedin')
			contact_us.objects.all().delete()
			contact_us.objects.create(
				address=address,
				contact_no=contact_no,
				gmail_id=gmail_id,
				facbook_id=facbook_id,
				instagram_id=instagram_id,
				twitter_id=twitter_id,
				linkedin_id=linkedin_id,
			)
			print(contact_us)
		dic = {
			'data':contact_us.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		dic.update(get_cart_len(request))
		dic.update(get_wishlist_len(request))
		return render(request, 'staff_app/contact.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_about_us(request):
	if check_user_authentication(request,'Staff'):
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
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/about-us.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_gallery(request):
	if check_user_authentication(request,'Staff'):
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
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/gallery.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def staff_blog(request):
	if check_user_authentication(request,'Staff'):
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
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/blog.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def staff_banner(request):
	if check_user_authentication(request,'Staff'):
		if request.method == 'POST':
			title = request.POST.get('title')
			print(title)
			sub_title = request.POST.get('sub_title')
			desc = request.POST.get('desc')
			link = request.POST.get('link')
			image = request.FILES.get('file')
			print(image, type(image))
			# HomeBanner.objects.all().delete()
			HomeBanner.objects.create(
				title=title,
				sub_title=sub_title,
				description=desc,
				link=link,
				image=image,

			)
		dic = {
			'data':HomeBanner.objects.all(),
			'notification':get_notifications(request.user),'categories':ProductCategory.objects.all(),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/banner.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def staff_subscription_pack(request):
	if check_user_authentication(request, 'Staff'):
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
			return redirect('/staffs/subscription-pack')
		dic = {'charge':SubscriptionCharge.objects.all(),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/subscription-charges.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def userSubscriptionRequest_staff(request):
	if request.user.role.level.level=='Staff':
		if request.method == 'GET':
			data = UserSubscriptionRequest.objects.all()
			dic={'data':data, 'categories':ProductCategory.objects.all(),}
			return render(request, 'staff_app/subscription-request.html', dic)


from django.contrib.auth.decorators import login_required
import random
from django.db import transaction
import datetime


login_required('/')
@csrf_exempt
def staffbalanacetransfer(request):
	print(request.user.email,'OTPPP')
	bal = Wallet.objects.get(user=request.user).current_balance
	userdata = UserData.objects.filter(is_active = True)
	vandordata = Vendor.objects.filter(is_active = True)
	transectiondata = WalletTransfer.objects.filter(user=request.user).order_by('-id')
	context = {
			'userdata':userdata,'vendordata': vandordata,
			'transectiodetails':transectiondata,
			'bal':bal,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False))
		}

	id = WalletTransferApproval.objects.all()[0:1]

	if id is not None:

		for id in id:

			print(id.id,'idddd')

	
			

	if WalletTransferApproval.objects.get(id =id.id).vendor == 1:

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
			notification(request.user, 'OTP sent successfully.')
			messages.success(request, 'OTP sent successfully.')
			return render(request,'staff_app/otpverify.html')
		return render(request,'staff_app/customerwallettransfer.html',context=context)
	else :
		messages.error(request,'Payments Mode off')
		return render(request,'staff_app/customerwallettransfer.html',context=context)


login_required('/')
@transaction.atomic
@csrf_exempt
def transfer_amount_staff(request):
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
				user = User.objects.get(username = request.session['recivername'])
				notification(user, 'Money Successfully Recived.')
				notification(request.user, 'Money Successfully Transfered')
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
	return render(request,'staff_app/otpverify.html')



@csrf_exempt
def staff_vendor_commission_wallet(request):
	if check_user_authentication(request, 'Staff'):
		dic = {
			'vendor_commission_wallet':Vendor_Wallet_Commission.objects.all(), 
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'staff_app/vendor_commission_wallet.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_vendor_commission_wallet_details(request, id):
	if check_user_authentication(request, 'Staff'):

		vendor_commission_wallet=Vendor_Wallet_Commission.objects.filter(id=id).first()
		vendor_commission_wallet_transaction = VendorWalletTransaction.objects.filter(vendor_wallet_commission=id)
		dic = {
            'vendor_commission_wallet':vendor_commission_wallet,
			'vendor_commission_wallet_transaction':vendor_commission_wallet_transaction,
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		
		}
		return render(request, 'staff_app/wallet_commission_dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def staff_activate_is_commission_wallet_vendor(request):
	if check_user_authentication(request, 'Staff'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		wallet = Vendor_Wallet_Commission.objects.get(id=id_)
		Vendor_Wallet_Commission.objects.filter(id=id_).update(is_active=True)
		sub = 'AVPL -Vendor Commission wallet activated Successfully'
		msg = '''Hi there!
Your AVPL Vendor Commission wallet activated Successfully, you can transaction.

Thanks!'''
		EmailMessage(sub,msg,to=[wallet.user.email]).send()
		messages.success(request, 'AVPL Vendor Commission wallet activated Successfully !!!!')
		notification(request.user, 'Vendor '+wallet.user.vendor.first_name+' '+wallet.user.vendor.last_name)
		notification(wallet.user, 'AVPL Vendor Commission wallet activated Successfully.')
		return redirect('/staffs/vendor-commission-wallet')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def staff_deactivate_is_commission_wallet_vendor(request):
	if check_user_authentication(request, 'Staff'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		wallet = Vendor_Wallet_Commission.objects.get(id=id_)
		Vendor_Wallet_Commission.objects.filter(id=id_).update(is_active=False)
		sub = 'AVPL -AVPL Vendor Commission wallet Deactivate Successfully'
		msg = '''Hi there!
Your AVPL Vendor Commission wallet Deactivate Successfully.

Thanks!'''
		EmailMessage(sub,msg,to=[wallet.user.email]).send()
		messages.success(request, 'AVPLVendor Commission wallet Deactivate Successfully !!!!')
		notification(request.user, 'Vendor '+wallet.user.vendor.first_name+' '+wallet.user.vendor.last_name)
		notification(wallet.user, 'AVPL Vendor Commission wallet Deactivate Successfully.')
		return redirect('/staffs/vendor-commission-wallet')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



