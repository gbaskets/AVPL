from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.http import HttpResponse
from vendor_app.models import *
from admin_app.models import *
from user_app.models import *
from main_app.models import *
import uuid
from main_app.utils import *
from main_app.mlm_utils import *
from main_app.level_plan_utils import *
from user_app.utils import *
from main_app.views import send_otp

from .forms import *

@csrf_exempt
def create_user(request):
	email = request.POST.get('email')
	password = request.POST.get('password')
	if User.objects.filter(email=email).exists():
		user = User.objects.get(email=email)
		messages.info(request,'User Already Exists')
		# return HttpResponse('Error : User Already Registered')
		return send_otp(request, 'User', user)

	else:
		#User.objects.create_user(email,email,password)
		User.objects.create_user(email = email, username= email, password =password)
		user = User.objects.get(email=email)
		Role(user=user, level=Levels.objects.get(level='User')).save()
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		gender = request.POST.get('gender')
		phone = request.POST.get('phone')
		# question = request.POST.get('question')
		# answer = request.POST.get('answer')
		zipcode = request.POST.get('zipcode')
		address = request.POST.get('adrs')
		gmaps = googlemaps.Client(key='AIzaSyBqBF76cMbvE_LREvm1S43LzZGxTsRQ0wA')
		if address:
			add_lat_long = gmaps.geocode(address)
			lat = add_lat_long[0]['geometry']['location']['lat']
			lng = add_lat_long[0]['geometry']['location']['lng']
			# lat = 28.7983
			# lng = 79.0220
			UserData.objects.create(
				user = user,
				first_name = first_name,
				last_name = last_name,
				phone = phone,
				address = address,
				zipcode = zipcode,
				latitude = lat,
				longitude = lng,
				gender = gender,
				
				# question = question,
				# answer = answer
			)
			return send_otp(request, 'User', user)
@csrf_exempt
@login_required(login_url='/login/')
def user_dashboard(request):
	if check_user_authentication(request, 'CUSTOMER'):
		customer_obj=Customer.objects.filter(user=request.user).first()
		if not Wallet.objects.filter(customer=customer_obj).exists():
			Wallet.objects.create(customer=customer_obj)
	
		dic = {
			
			# 'tree':fetch_empty_nodes(request.user),
			# 'referrals':referals,
			# 'pv':fetch_pv(request.user),
			'wallet':Wallet.objects.filter(customer=customer_obj).first(),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/dashboard.html', dic)
	else:
		return render(request, '403.html')

		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def user_create_link(request):
	if check_user_authentication(request, 'CUSTOMER'):
		referal_obj = Level_Plan_Referrals.objects.filter(referrals__id=request.user.id).first()
		referals = Level_Plan_Referrals.objects.filter(level_plan_referral=referal_obj)
		flag = False
		try:
			mlm = MLM.objects.get(node=request.user)
			
			if mlm.left == None or mlm.right == None:
				flag = True
		except MLM.DoesNotExist:
			user = None
		dic = {
			
			'flag':flag,
			'referal':referals,
			'tree':fetch_empty_nodess(request.user),
			
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		tree=fetch_empty_nodess(request.user)
		print(tree,'TTTTTTTTTTTTT')
		return render(request, 'user_app/create-link.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def user_generate_link_left(request):
	if check_user_authentication(request, 'CUSTOMER'):
		data = {'link':generate_link(request.user, 'User','left')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})
@csrf_exempt
def user_generate_link_right(request):
	if check_user_authentication(request, 'CUSTOMER'):
		data = {'link':generate_link(request.user, 'User','right')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})
@csrf_exempt
def user_generate_link_2_left(request):
	if check_user_authentication(request, 'CUSTOMER'):
		user = User.objects.get(id=request.GET.get('user'))
		data = {'link':generate_link(user, 'User','left')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})
@csrf_exempt
def user_generate_link_2_right(request):
	if check_user_authentication(request, 'CUSTOMER'):
		user = User.objects.get(id=request.GET.get('user'))
		data = {'link':generate_link(user, 'User','right')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})


@csrf_exempt
def direct_referal(request):
	if check_user_authentication(request, 'CUSTOMER'):
		flag = False
		referal_pv = 0
		mlm = MLM.objects.filter(parent=request.user)
		mlm = []
		for i in MLM.objects.filter(parent=request.user):
			mlm.append(i)
		user_data = []
		for i in mlm:
			user_data.append({i:UserData.objects.get(user__username=i).pv})
		for i in mlm:
			if UserData.objects.filter(user__username=i):
				referal_pv = referal_pv + UserData.objects.get(user__username=i).pv
		redeem_amount = referal_pv*(DirectReferalCommission.objects.all()[0].percentage/100 if DirectReferalCommission.objects.all() else 0 )
		dic = {
			'mlm':MLM.objects.filter(parent=request.user),
			'user_data':user_data,
			'flag':flag,
			'redeem_amount':redeem_amount,
			'referal_pv':referal_pv,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		return render(request, 'user_app/direct_referal.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def referal_transaction(request):
	if check_user_authentication(request, 'CUSTOMER'):
		flag = False
		referal_pv = 0
		mlm = MLM.objects.filter(parent=request.user)
		mlm = []
		for i in MLM.objects.filter(parent=request.user):
			mlm.append(i)
		user_data = []
		print(mlm)
		for i in mlm:
			user_data.append({i:UserData.objects.get(user__username=i).pv})
		for i in mlm:
			if UserData.objects.filter(user__username=i):
				referal_pv = referal_pv + UserData.objects.get(user__username=i).pv
		redeem_amount = referal_pv*(DirectReferalCommission.objects.all()[0].percentage/100)
		print(redeem_amount)
		make_wallet_transaction(request.user, redeem_amount, 'CREDIT')
		dic = {
			'mlm':MLM.objects.filter(parent=request.user),
			'user_data':user_data,
			'flag':flag,
			'redeem_amount':redeem_amount,
			'referal_pv':referal_pv,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		return render(request, 'user_app/direct_referal.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')





@csrf_exempt
def user_add_to_cart(request):
	print('=====user')
	if check_user_authentication(request, 'CUSTOMER'):
		print(request.user)
		variants = request.POST.getlist('variants[]')
		quantity = request.POST.get('quantity')
		product = Product.objects.get(id=request.POST.get('product'))
		print(product)
		flag = True
		print(product.stock)
		if product.stock >= int(quantity):
			print('hellllo')
			if True:
					print("fggd")
				
					if Cart.objects.filter(user=request.user).exists():
						print("bjhbjhgjh")
						cart = Cart.objects.get(user=request.user)
						allow = True
						for x in CartItems.objects.filter(cart=cart):
							print("jhvghvgf")
							if x.product.store == product.store:
								
								allow = True
								print(allow)
								break
							else:
								allow = False
								print(allow)
								break
						if allow:
							print("jhvhfty")
							variant_matched = False
							item = ''
							for items in CartItems.objects.filter(cart=cart, product=product):
								cart_variants = []
								print(cart_variants,"cart_variants")
								for x in CartItemVariant.objects.filter(cartitem=items):
									print("cccccc",x)
									cart_variants.append(str(x.product_variant.id))
								if variants == cart_variants:
									variant_matched = True
									item = items
									break
							if variant_matched:
								new_quantity = int(quantity) + item.quantity
								print(new_quantity,'hhhhhhhhhhhhhhhh')
								if new_quantity > product.stock:
									new_quantity = product.stock
								price = item.product.price
								total_price = item.product.price * new_quantity
								CartItems.objects.filter(id=item.id).update(
									quantity = new_quantity,
									per_item_cost = price,
									total_cost = total_price
								)
								subtotal = cart.subtotal + (int(quantity)*item.product.price)
								Cart.objects.filter(user=request.user).update(subtotal=subtotal)
								calculate_cart_tax(request)
								return JsonResponse({'response':'product already in cart !', 'cart_len':get_cart_len(request)})
							else:
								if int(quantity) > product.stock:
									quantity = product.stock
								item = CartItems.objects.create(
										cart = cart,
										product = product,
										quantity = quantity,
										per_item_cost = product.price,
										total_cost = product.price*int(quantity)
									)
								for x in variants:
									print("xxxxx",x)
									CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
								subtotal = cart.subtotal + (int(quantity)*product.price)
								Cart.objects.filter(user=request.user).update(subtotal=subtotal)
								print("prining here")
								print(subtotal)
								calculate_cart_tax(request)
								return JsonResponse({'response':'product added successfully !', 'cart_len':get_cart_len(request)})
						else:
							# if int(quantity) > product.stock:
							# 	quantity = product.stock
							# print(quantity)
							# item = CartItems.objects.create(
							# 	cart = cart,
							# 	product = product,
							# 	quantity = quantity,
							# 	per_item_cost = product.price,
							# 	total_cost = product.price*int(quantity)
							# )
							# print(item,'iiiiiiiiiiiiiiiii')
							# for x in variants:
							# 	print("xxxxx",x)
							# 	CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
							# subtotal = cart.subtotal + (int(quantity)*product.price)
							# Cart.objects.filter(user=request.user).update(subtotal=subtotal)
							# print("prining here")
							# print(subtotal)
							# calculate_cart_tax(request)
							messages.info(request, 'Add Product from same store.')
							print("==================>Add Product from same store")
							return JsonResponse({'response': 'Add Product from same store !'})
						return render(request, 'usertemplate/index.html')
						# else:
						# 	return JsonResponse({'response':'failed2', 'cart_len':get_cart_len(request)})
					else:
						if int(quantity) > product.stock:
								quantity = product.stock
						cart = Cart.objects.create(user=request.user)
						total = product.price*int(quantity)
						item = CartItems.objects.create(
							cart = Cart.objects.get(user=request.user),
							product = product,
							quantity = quantity,
							per_item_cost = product.price,
							total_cost = total
						)
						for x in variants:
							print("rerwe", x)
							CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
						Cart.objects.filter(user=request.user).update(subtotal=total)	
						calculate_cart_tax(request)
						return JsonResponse({'response':'success', 'cart_len':get_cart_len(request)})
		return JsonResponse({'response':'failed'})
	else:
		return JsonResponse({'response': 'Login to continue'})
		print('jello')
		return render(request, '403.html')

# wishlist
@csrf_exempt
def add_to_wishlist(request):
	if check_user_authentication(request, 'CUSTOMER'):
		variants = request.POST.getlist('variants[]')
		quantity = request.POST.get('quantity')
		product = Product.objects.get(id=request.POST.get('product'))
		print(product)
		flag = True
		if product.stock >= int(quantity):
			if True:
					print("fggd")
				
					if Wishlist.objects.filter(user=request.user).exists():
						print("bjhbjhgjh")
						wishlist = Wishlist.objects.get(user=request.user)
						allow = True
						for x in WishlistItems.objects.filter(wishlist=wishlist):
							print("jhvghvgf")
							if x.product.store == product.store:
								allow = True
								break
							else:
								allow = False
								break
						if allow:
							print("jhvhfty")
							variant_matched = False
							item = ''
							print(item)
							for items in WishlistItems.objects.filter(wishlist=wishlist, product=product):
								wishlist_variants = []
								print(wishlist_variants,"wishlist_variants")
								for x in WishlistItemVariant.objects.filter(wishlistitem=items):
									print("cccccc",x)
									wishlist_variants.append(str(x.product_variant.id))
								if variants == wishlist_variants:
									variant_matched = True
									item = items
									break
							if variant_matched:
								new_quantity = int(quantity) + item.quantity
								if new_quantity > product.stock:
									new_quantity = product.stock
								price = item.product.price
								print(price,'KKKKKKKKKKKK')
								total_price = item.product.price * new_quantity
								WishlistItems.objects.filter(id=item.id).update(
									quantity = new_quantity,
									per_item_cost = price,
									total_cost = total_price
								)
								subtotal = wishlist.subtotal + (int(quantity)*item.product.price)
								Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
							else:
								if int(quantity) > product.stock:
									quantity = product.stock
								item = WishlistItems.objects.create(
									wishlist = wishlist,
									product = product,
									quantity = quantity,
									per_item_cost = product.price,
									total_cost = product.price*int(quantity)
								)
								for x in variants:
									print("xxxxx",x)
									WishlistItemVariant.objects.create(wishlist=wishlist, wishlistitem=item, product_variant=ProductVariant.objects.get(id=x))
								subtotal = wishlist.subtotal + (int(quantity)*product.price)
								Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
								print("prining here")
								print(subtotal)
								# calculate_wishlist_tax(request)
								return JsonResponse({'response':'success', 'wishlist_len':get_wishlist_len(request)})
								# calculate_wishlist_tax(request)
						else:
							if int(quantity) > product.stock:
								quantity = product.stock
							item = WishlistItems.objects.create(
								wishlist = wishlist,
								product = product,
								quantity = quantity,
								per_item_cost = product.price,
								total_cost = product.price*int(quantity)
							)
							for x in variants:
								print("xxxxx",x)
								WishlistItemVariant.objects.create(wishlist=wishlist, wishlistitem=item, product_variant=ProductVariant.objects.get(id=x))
							subtotal = wishlist.subtotal + (int(quantity)*product.price)
							Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
							print("prining here")
							print(subtotal)
							# calculate_wishlist_tax(request)
						return JsonResponse({'response':'success', 'wishlist_len':get_wishlist_len(request)})
						# else:
						# 	return JsonResponse({'response':'failed2', 'wishlist_len':get_wishlist_len(request)})
					else:
						if int(quantity) > product.stock:
								quantity = product.stock
						wishlist = Wishlist.objects.create(user=request.user)
						total = product.price*int(quantity)
						item = WishlistItems.objects.create(
							wishlist = Wishlist.objects.get(user=request.user),
							product = product,
							quantity = quantity,
							per_item_cost = product.price,
							total_cost = total
						)
						for x in variants:
							print("rerwe", x)
							WItemVariant.objects.create(wishlist=wishlist, wishlistitem=item, product_variant=ProductVariant.objects.get(id=x))
						Wishlist.objects.filter(user=request.user).update(subtotal=total)
						# calculate_wishlist_tax(request)
						return JsonResponse({'response':'success', 'wishlist_len':get_wishlist_len(request)})
		return JsonResponse({'response':'failed'})
	else:
		return JsonResponse({'response': 'Login to continue'})
		return render(request, '403.html')
@csrf_exempt
@login_required(login_url='/login/')
def user_wishlist(request):
	if check_user_authentication(request, 'CUSTOMER'):
		categories = ProductCategory.objects.all()
		if Wishlist.objects.filter(user=request.user).exists():
			dic = get_wishlist_items(request)
			if len(WishlistItems.objects.filter(wishlist=Wishlist.objects.get(user=request.user))) == 0:
				empty = True
			else:
				empty = False
			stock_out = False
			for x in dic['items']:
				if x['stock_out']:
					stock_out = True
					break
			dic.update({'empty':empty, 'stock_out':stock_out})
			dic.update(get_cart_len(request))
			dic.update({
				        'contact_us':contact_us.objects.all()[0],
						'categories':categories,
						'notification':get_notifications(request.user),
						'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					})
			return render(request, 'usertemplate/wishlist.html', dic)
		else:
			dic = {'empty':True}
			dic.update(get_dic(request))
			dic.update(get_cart_len(request))
			dic.update({
							'categories':categories,
						'notification':get_notifications(request.user),
						'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					})
			return render(request, 'usertemplate/wishlist.html', dic)
	else:
		
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
@login_required(login_url='/login/')
def user_cart(request):
	if check_user_authentication(request, 'CUSTOMER'):
		categories = ProductCategory.objects.all()
		if Cart.objects.filter(user=request.user).exists():
			dic = get_cart_items(request)
			if len(CartItems.objects.filter(cart=Cart.objects.get(user=request.user))) == 0:
				empty = True
			else:
				empty = False
			stock_out = False
			for x in dic['items']:
				if x['stock_out']:
					stock_out = True
					break
			dic.update({'empty':empty, 'stock_out':stock_out})
			dic.update({
				'categories':categories,
				# 'notification':get_notifications(request.user),
				# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				})
			dic.update(get_wishlist_len(request))
			print(dic)
			return render(request, 'usertemplate/cart.html', dic)
		else:
			dic = {'empty':True}
			dic.update(get_dic(request))
			dic.update({
				'contact_us':contact_us.objects.all()[0],
				'categories':categories,
				'wish_len':get_wishlist_len(request),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				})
			return render(request, 'usertemplate/cart.html', dic)
	else:
		
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
@login_required(login_url='/login/')
def update_cart_item(request):
	cart = Cart.objects.get(user=request.user)
	print("cart=>", cart)
	item = CartItems.objects.get(id=request.GET.get('item'))
	print("item", item)
	new_quantity = int(request.GET.get('quantity'))
	if new_quantity > item.quantity:
		print('1')
		updated_quantity = new_quantity - item.quantity
		total_price = item.total_cost + (item.product.price * updated_quantity)
		price = item.product.price
		CartItems.objects.filter(id=request.GET.get('item')).update(
			quantity = new_quantity,
			per_item_cost = price,
			total_cost = total_price
		)
		subtotal = cart.subtotal + (updated_quantity*price)
		Cart.objects.filter(user=request.user).update(subtotal=subtotal)
		calculate_cart_tax(request)
	else:
		print('2')
		updated_quantity = item.quantity - new_quantity
		total_price = item.total_cost - (item.product.price * updated_quantity)
		price = item.product.price
		CartItems.objects.filter(id=request.GET.get('item')).update(
			quantity = new_quantity,
			per_item_cost = price,
			total_cost = total_price
		)
		subtotal = cart.subtotal - (int(updated_quantity)*item.product.price)
		Cart.objects.filter(user=request.user).update(subtotal=subtotal)
		calculate_cart_tax(request)
	cart = Cart.objects.get(user=request.user)
	dic = {
		'item_total':CartItems.objects.get(id=request.GET.get('item')).total_cost,
		'subtotal':cart.subtotal,
		'tax':cart.tax,
		'delivery':cart.delivery_charges,
		'total':cart.total
	}
	return JsonResponse(dic)
@csrf_exempt
@login_required(login_url='/login/')
def remove_cart_item(request):
	cart = Cart.objects.get(user=request.user)
	item = CartItems.objects.get(id=request.GET.get('item'))
	subtotal = cart.subtotal - item.total_cost
	CartItemVariant.objects.filter(cartitem=CartItems.objects.get(id=request.GET.get('item'))).delete()
	CartItems.objects.filter(id=request.GET.get('item')).delete()
	Cart.objects.filter(user=request.user).update(subtotal=subtotal)
	calculate_cart_tax(request)
	cart = Cart.objects.get(user=request.user)
	if len(CartItems.objects.filter(cart=cart)) == 0:
		empty = '1'
	else:
		empty = '0'
	dic = {
		'subtotal':cart.subtotal,
		'tax':cart.tax,
		'delivery':cart.delivery_charges,
		'total':cart.total,
		'empty':empty
	}
	return JsonResponse(dic)
@csrf_exempt
@login_required(login_url='/login/')
def remove_wishlist_item(request):
	wishlist = Wishlist.objects.get(user=request.user)
	item = WishlistItems.objects.get(id=request.GET.get('item'))
	subtotal = wishlist.subtotal - item.total_cost
	WishlistItemVariant.objects.filter(wishlistitem=WishlistItems.objects.get(id=request.GET.get('item'))).delete()
	WishlistItems.objects.filter(id=request.GET.get('item')).delete()
	Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
	wishlist = Wishlist.objects.get(user=request.user)
	if len(WishlistItems.objects.filter(wishlist=wishlist)) == 0:
		empty = '1'
	else:
		empty = '0'
	dic = {
		'subtotal':wishlist.subtotal,
		'tax':wishlist.tax,
		'delivery':wishlist.delivery_charges,
		'total':wishlist.total,
		'empty':empty
	}
	return JsonResponse(dic)

@csrf_exempt
@login_required(login_url='/login/')
def my_address(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			location = request.POST.get('location')
			name = request.POST.get('name')
			home_no = request.POST.get('home_no')
			landmark = request.POST.get('landmark')
			city = request.POST.get('city')
			pincode = request.POST.get('pincode')
			state = request.POST.get('state')
			contact = request.POST.get('contact')
			if len(Address.objects.filter(customer__user=request.user)) == 0:
				default = True
			else:
				default = False
			gmaps = googlemaps.Client(key='AIzaSyCEjY246d9MYQIe69nPzV_ceogrpglpY0Q')
			if location:
				# add_lat_long = gmaps.geocode(location)
				# lat = add_lat_long[0]['geometry']['location']['lat']
				# lng = add_lat_long[0]['geometry']['location']['lng']
				lat = 28.7983
				lng = 79.0220
				customer_obj=Customer.objects.filter(user=request.user).first()
				Address.objects.create(
					customer = customer_obj,
					latitude = lat,
					longitude = lng,
					name = name,
					home_no = home_no,
					landmark = landmark,
					city = city,
					pincode = pincode,
					state = state,
					contact = contact,
					default = default
				)
				messages.success(request, 'Address Added Successfully !!!!')
			code = ''
			for x in Address.objects.filter(customer__user=request.user):
				code = code + '<tr>'
				code = code + '<td>'+x.name+'</td>'
				code = code + '<td>'+x.home_no+'</td>'
				code = code + '<td>'+x.landmark+'</td>'
				code = code + '<td>'+x.city+'</td>'
				code = code + '<td>'+x.pincode+'</td>'
				code = code + '<td>'+x.state+'</td>'
				code = code + '<td>'+x.contact+'</td>'
				code = code + '</tr>'
			dic = {'data':code, 'msg':'Address Added Successfully !!!!'}
			
			# return JsonResponse(dic)
		return render(request, 'user_app/my-address.html', {"customer_obj":Customer.objects.filter(user=request.user).first() ,'data':Address.objects.filter(customer__user=request.user)})
	else:
		return render(request, '403.html')
@csrf_exempt
@login_required(login_url='/login/')
def user_set_default_address(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'GET':
			id_ = request.GET.get('id')
			Address.objects.filter(customer__user=request.user).update(default=False)
			Address.objects.filter(id=id_).update(default=True)
			address = Address.objects.get(id=id_)
			code = address.name+'<span id="span" style="background-color:green;color:white;padding-right:5px;padding-left:5px;border-radius:50px;">DEFAULT</span>'
			return HttpResponse(code)
	else:
		return render(request, '403.html')

@csrf_exempt
@login_required(login_url='/login/')
def add_new_address(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			location = request.POST.get('location')
			name = request.POST.get('name')
			home_no = request.POST.get('home_no')
			landmark = request.POST.get('landmark')
			city = request.POST.get('city')
			pincode = request.POST.get('pincode')
			state = request.POST.get('state')
			contact = request.POST.get('contact')
			if len(Address.objects.filter(user=request.user)) == 0:
				default = True
			else:
				default = False
			gmaps = googlemaps.Client(key='AIzaSyCEjY246d9MYQIe69nPzV_ceogrpglpY0Q')
			if location:
				# add_lat_long = gmaps.geocode(location)
				# lat = add_lat_long[0]['geometry']['location']['lat']
				# lng = add_lat_long[0]['geometry']['location']['lng']
				lat= 28.7983
				lng = 79.0220
				Address.objects.create(
					user = request.user,
					latitude = lat,
					longitude = lng,
					name = name,
					home_no = home_no,
					landmark = landmark,
					city = city,
					pincode = pincode,
					state = state,
					contact = contact,
					default = default
				)
			return redirect('/selectaddress/?cart='+request.session['cart_id'])
		return render(request, 'user_app/my-address.html', {"customer_obj":Customer.objects.filter(user=request.user).first(), 'data':Address.objects.filter(user=request.user)})
	else:
		return render(request, '403.html')
@csrf_exempt
@login_required(login_url='/login/')
def my_order(request):
	if check_user_authentication(request, 'CUSTOMER'):
		store_id = request.GET.get('store')
		orders = []
		if store_id:
			store = Store.objects.get(id=store_id)
		# 	orders = get_my_orders(request.user, store)
		# else:
		# 	orders = get_my_orders(request.user)
		dic = {
			"customer_obj":Customer.objects.filter(user=request.user).first(),
			# 'orders':orders,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/my_order.html', dic)
	else:
		return render(request, '403.html')


def enable_self_pickup(request):
	check = request.GET.get('self')
	if check == '1':
		Cart.objects.filter(id=request.GET.get('c')).update(self_pickup=True)
	else:
		Cart.objects.filter(id=request.GET.get('c')).update(self_pickup=False)
	calculate_cart_tax(request)
	return JsonResponse({'response':'success'})

@csrf_exempt
@login_required(login_url='/login/')
def save_location(request):
	if check_user_authentication(request, 'CUSTOMER'):
		address = request.GET.get('location')
		gmaps = googlemaps.Client(key='AIzaSyBqBF76cMbvE_LREvm1S43LzZGxTsRQ0wA')
		if address:
			add_lat_long = gmaps.geocode(address)
			lat = add_lat_long[0]['geometry']['location']['lat']
			lng = add_lat_long[0]['geometry']['location']['lng']
		UserData.objects.filter(user=request.user).update(
			latitude=lat,
			longitude=lng
		)
		return JsonResponse({'response':'success'})
@csrf_exempt
@login_required(login_url='/login/')
def user_wallet(request):
	if check_user_authentication(request, 'CUSTOMER'):
		customer_obj=Customer.objects.filter(user=request.user).first()
		if not Wallet.objects.filter(customer=customer_obj).exists():
			Wallet.objects.create(customer=customer_obj)
		dic = {"customer_obj":Customer.objects.filter(user=request.user).first(),
			'wallet':Wallet.objects.filter(customer=customer_obj).first(),
			'wallet_transactions':WalletTransaction.objects.filter(wallet=Wallet.objects.filter(customer=customer_obj).first()).order_by('-transactiondate'),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/wallet-dash.html', dic)
	else:
		return render(request, '403.html')
@csrf_exempt
def user_pv_wallet(request):
	if check_user_authentication(request, 'CUSTOMER'):
		print(UserData.objects.get(user=request.user).pv,'PPPPPPPPPPPPPP')
		dic = {"customer_obj":Customer.objects.filter(user=request.user).first(),
			'pv':fetch_pv(request.user),
			'transactions':fetch_pv_transactions(request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/pv.html', dic)
	else:
		return render(request, '403.html')
@csrf_exempt
def genealogyTree_binary(request):
	if check_user_authentication(request, 'CUSTOMER'):
		tree=fetch_user_tree(request.user)
		treesss=fetch_empty_nodes(request.user)
		print(treesss,'TTTT')
		# print(treesss['left'],'LLLLLLLLLLLLLLLLLLLLLLLLLL')
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
	
		
		node=MLM.objects.filter(node=request.user)
		node_V=MLM.objects.filter(node=request.user).first()
		
		usrpv = UserPV.objects.get(user=request.user)
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
						"customer_obj":Customer.objects.filter(user=request.user).first(),
						'tree':fetch_user_tree(request.user),
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

						'user':request.user,
						'notification':get_notifications(request.user),
						'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
							}
				else:
					print('None')
					dic = {
					 "customer_obj":Customer.objects.filter(user=request.user).first(),
					'tree':fetch_user_tree(request.user),
					'nodel':nodel,
					'noder':noder,
					'trees':node,
					'nodes1':nodes1,
					'nodes2':nodes2,
					'nodes3':nodes3,
					'nodes4':nodes4,
				
					
					
					'user':request.user,
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
						}
			else:
				print('None')
				dic = {
					 "customer_obj":Customer.objects.filter(user=request.user).first(),
					'tree':fetch_user_tree(request.user),
					'nodel':nodel,
					'noder':noder,
					'trees':node,

					'nodes1':nodes1,
					'nodes2':nodes2,
					'nodes3':nodes3,
					'nodes4':nodes4,
					
					
					
					'user':request.user,
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
						}
			return render(request, 'user_app/genealogyTree_binary.html',dic)
		if node_V.left  is not None:	
			return render(request, 'user_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv,'usrpvl':usrpvl,'nodel':nodel,
						'noder':noder,})
		
		if node_V.right is not None:					
		    return render(request, 'user_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv,'usrpvr':usrpvr,
						})
		else:
			print('None')
			return render(request, 'user_app/genealogyTree_binary.html',{'trees':node,'usrpv':usrpv})
	else:
		return render(request, '403.html')

@csrf_exempt
def genealogyTree_level(request):
	if check_user_authentication(request, 'CUSTOMER'):
		sponser =Level_Plan_Sponsors.objects.all()
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
				"customer_obj":Customer.objects.filter(user=request.user).first(),
				'referals':referals,'usrpv':usrpv,
				'sponser_r':referal_obj.referrals,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				'referals_user':referals_user,
				
			}
			return render(request, 'user_app/genealogyTree_level.html',dic)
			
			
		if referal_obj or referalss  is not None:	
			
		
			dic = {
				"customer_obj":Customer.objects.filter(user=request.user).first(),
				'referals':referals,'usrpv':usrpv,
				'sponser_r':referal_obj.referrals,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}

		
		else:
			print('none')
			dic = {
				"customer_obj":Customer.objects.filter(user=request.user).first(),
				'referals':referals,'usrpvs':usrpvs,
				'sponser_r':referal_obj,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
		return render(request, 'user_app/genealogyTree_level.html',dic)
	else:
		return render(request, '403.html')
@csrf_exempt
def user_tree(request):
	if check_user_authentication(request, 'CUSTOMER'):
	
		dic = {
			"customer_obj":Customer.objects.filter(user=request.user).first(),
			'tree':fetch_user_tree(request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/tree.html', dic)
	else:
		return render(request, '403.html')

@csrf_exempt
def user_save_product_rating(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			product = Product.objects.get(id=request.POST.get('product'))
			rating = request.POST.get('rating')
			print(rating)
			review  = request.POST.get('review')
			print(review)
			user = request.user
			if not ProductRating.objects.filter(user=user, product=product).exists():
				ProductRating.objects.create(user=user, product=product, rating=rating, review=review)
			else:
				ProductRating.objects.update(user=user, product=product, rating=rating, review=review)
			return redirect('/user/myorder')
	else:
		return render(request, '403.html')

@csrf_exempt
def user_withdraw(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			amount = float(request.POST.get('amount'))
			print(amount,'AAAAAAAAAAAA')
			if amount < 500:
				messages.success(request, 'Withdrawl amount must be greater than 500.')
				return redirect('/user/withdraw')
			flag = True
			for x in UserWithdrawRequest.objects.filter(user=request.user):
				if x.is_active == 0 or x.is_active == 1:
					flag = False
					break
			if flag:
				tds = ((amount/100)*5)
				credited_amount = amount - tds
				withdraw=UserWithdrawRequest.objects.create(
					user = request.user,
					request_date = timezone.now(),
					amount = amount,
					credited_amount = credited_amount,
					tds = tds
				)
				make_wallet_transaction(withdraw.user, (withdraw.amount), 'DEBIT')
				messages.success(request, 'We have received your payment withdraw request. Your payment wil be credited in your account in 3 working days after approval.')
				return redirect('/user/withdraw')
			else:
				messages.success(request, 'You already have a withdrawl request pending, please wait for it to credit.')
				return redirect('/user/withdraw')
		flag = True
		if PaymentInfo.objects.filter(user=request.user).exists():
			flag = True
		else:
			flag = False
		if not Wallet.objects.filter(user=request.user).exists():
			Wallet.objects.create(user=request.user)
		if not CreditedMoney.objects.filter(user=request.user).exists():
			CreditedMoney.objects.create(user=request.user)

		if not TDS_Log_Wallet.objects.filter(user=request.user).exists():
			TDS_Log_Wallet.objects.create(user=request.user)

	
		dic = {
			'user':UserData.objects.filter(user=request.user).first(),
			'flag':flag,
			'wallet':Wallet.objects.filter(user=request.user).first(),
			'data':UserWithdrawRequest.objects.filter(user=request.user),
			'creditedlimit':CreditedMoney.objects.filter(user=request.user).first(),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/withdraw.html', dic)
	else:
		return render(request, '403.html')


@csrf_exempt
def user_save_paymentinfo(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			pan = request.FILES['pan']
			aadhar = request.FILES['aadhar']
			number = request.POST.get('number')
			name = request.POST.get('name')
			ifsc = request.POST.get('ifsc')
			if not PaymentInfo.objects.filter(user=request.user).exists():
				PaymentInfo.objects.create(
					user = request.user,
					account_no = number,
					bank_name = name,
					ifsc = ifsc,
					pan = pan,
					aadhar = aadhar
				)
			messages.success(request, 'Payment Details Saved Successfully')
			return redirect('/user/withdraw')
	else:
		return render(request, '403.html')

@csrf_exempt
def user_help(request):
	if check_user_authentication(request, 'CUSTOMER'):
		user=User.objects.filter(username='admin').first()
		print(user,'UUUUUU')
		if request.method == 'POST':
			subject = request.POST.get('subject')
			message = request.POST.get('message')
			if 'image' in request.FILES:
				image = request.FILES['image']
			else:
				image=''
			# query_obj=Query.objects.create(user=request.user, query_date=timezone.now(), subject=subject, message=message)
			# if image:
			# 	query_obj.image=image
			# query_obj.save()
			messages.success(request, 'Query Received')
			user=User.objects.filter(username='admin').first()
			print(user,'UUUUUU')
			notification(user,'New Query Received')
			return redirect('/user/help')
		dic = {
			"customer_obj":Customer.objects.filter(user=request.user).first(),
			# 'queries':Query.objects.filter(user=request.user),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/help.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def user_product_query(request):
	if check_user_authentication(request, 'CUSTOMER'):
		order = OrderItems.objects.get(id=request.GET.get('order'))
		dic = {
			'order':order,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/product-query.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def user_cancel_order(request):
	if check_user_authentication(request, 'CUSTOMER'):
		order = OrderItems.objects.get(id=request.GET.get('order'))
		# reason = OrderItems.objects.get(reason)
		dic = {
			'order':order,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/cancel-order.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def cancel_confirm(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			order_id = request.POST.get('order_id')
			print(order_id)
			reason = request.POST.get('reason')
			print(reason)
			obj = OrderItems.objects.get(id=order_id, order__user__username=request.user)
			obj.cancelled_on = timezone.now()
			obj.cancellation_reason = reason
			obj.delivery_is_active = 'Cancelled'
			if obj:
				obj.save()
				print(obj)
				messages.success(request, 'Order Cancelled!')
				dic = {
					"customer_obj":Customer.objects.filter(user=request.user).first(),
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					}
				notification(request.user, 'Order Cancelled Successfully!')
				return redirect('/user/myorder', dic)
			else:
				print('hello')
				dic = {
					"customer_obj":Customer.objects.filter(user=request.user).first(),
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					}
				messages.error(request, 'Please enter Valid data.')
				return redirect('/user/myorder', dic)
			# except:
			# 	print('hnhjhj')
			# 	return render(request, 'user_app/my_order.html')
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def user_generate_invoice(request):
	if check_user_authentication(request, 'CUSTOMER'):
		order = OrderItems.objects.get(id=request.GET.get('i'))
		dic = {
			'order':order
		}
		return render_to_pdf('main_app/invoice.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def create_vendor_link(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if UserVendorRelation.objects.filter(user=request.user).exists():
			dic = {
			"customer_obj":Customer.objects.filter(user=request.user).first(),
			'vendor_user':UserVendorRelation.objects.filter(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		else:
			dic = {
			"customer_obj":Customer.objects.filter(user=request.user).first(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		print("printing user")
		print(UserData.objects.get(user=request.user).user.usr.first_name)
		return render(request, 'user_app/create-vendor-link.html',dic)
	else:
		return HttpResponse('404 Not Found')
@csrf_exempt
def user_vendor_generate_link(request):
	if check_user_authentication(request, 'CUSTOMER'):
		data = {'link':generate_link(request.user, 'Vendor','left')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})

@csrf_exempt
def subscription_amount(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			amt = float(amount) / 100
			receipt = Memberip_Receipt.objects.create(user=request.user, amount=amt)
			data = create_razorpay_order2(str(receipt.id), request.user, amount)
			return JsonResponse({'data':data})
		else:
			month = request.GET.get('month')
			sub = SubscriptionCharge.objects.all()
			if len(sub) > 0:
				sub = sub[0]
				if month == '1':
					dic = {'amount':sub.one_month_subscription_charge}
					return JsonResponse(dic)
				elif month == '3':
					dic = {'amount':sub.three_month_subscription_charge}
					return JsonResponse(dic)
				elif month == '6':
					dic = {'amount':sub.six_month_subscription_charge}
					return JsonResponse(dic)
				elif month == '12':
					dic = {'amount':sub.twelve_month_subscription_charge}
					return JsonResponse(dic)
				else:
					return JsonResponse({'amount':'0.0'})
			else:
				return JsonResponse({'amount':'Error'})
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def capture_recharge_payment(request):
	if request.method == 'POST':
		payment_id = request.POST.get('razorpay_payment_id')
		order_id = request.POST.get('razorpay_order_id')
		signature = request.POST.get('razorpay_signature')
		receipt = Memberip_Receipt.objects.get(razorpay_order_id=order_id)
		razorpaytransaction = RazorpayTransaction.objects.create(payment_id=payment_id, order_id=order_id, signature=signature)
		receipt.payment_id = payment_id
		receipt.is_active = True
		receipt.save()
		#make_business_limit_transaction(request.user.vendor, receipt.amount, 'CREDIT', 'Recharge Receipt ID '+str(receipt.id))
		#below vendor recharge amount credit in admin wallet
		#Transaction goes to Admin wallet
		make_commission_transaction(request.user, receipt.amount, 'CREDIT')
		if Membership.objects.filter(user = request.user).exists():
			Membership.objects.filter(user = request.user).delete()
		Membership.objects.create(user = request.user)
		UserData.objects.filter(user = request.user).update(subscribed = True)
		sub = 'AVPL - Subscription '
		msg = '''Hi there!
Your Subscription has been successfully completed with amount Rs '''+str(receipt.amount)+'''.

Thanks!'''
		EmailMessage(sub, msg, to=[request.user.email]).send()
		notification(request.user, 'Subscription Successfully.')
		return render(request, 'user_app/subscription-success.html')
	else:
		return HttpResponse('Failed')

@csrf_exempt
def vendor_list(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'GET':
			vendors = User.objects.all()
			return render(request, 'user_app/vendor-list.html', {'vendors':vendors})
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def subscriptionRequest(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == "POST":
			if not UserSubscriptionRequest.objects.filter(user=request.user, is_active=False).exists():
				vendor_id = request.POST.get('key')
				amount = request.POST.get('amount')
				month = request.POST.get('month')
				vendor = Vendor.objects.get(id = vendor_id)
				UserSubscriptionRequest.objects.create(
					user = request.user,
					vendor = vendor,
					amount = amount,
					month = month
				)
				return JsonResponse({'success':"success"})
			else:
				msg ="You have already requested for plus membership"
				return HttpResponse(msg)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def user_billing_request(request):
	if check_user_authentication(request, 'CUSTOMER'):
		if request.method == 'POST':
			store = Store.objects.get(id=request.POST.get('store_id'))
			amount = request.POST.get('amount')
			plan = request.POST.get('plan')
			Billing_Request.objects.create(
				user = request.user,
				store = store,
				amount = amount,
				plan = plan
			)
			messages.success(request, 'Billing Request Created Successfully')
			return redirect('/user/billing/request/')
		dic = {'stores':fetch_vendors(request.session.get('lat'), request.session.get('lng')), 'requests':Billing_Request.objects.filter(user=request.user, is_active=False)}
		return render(request, 'user_app/billing-request.html', dic)
	return render(request, '403.html')
	# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def user_tds_withdraw(request):
	if check_user_authentication(request, 'CUSTOMER'):
		customer_obj=Customer.objects.filter(user=request.user).first()
		if not TDSLogWallet.objects.filter(customer=customer_obj).exists():
			TDSLogWallet.objects.create(customer=customer_obj)

		dic = {
			'tds_log':TDSLogWallet.objects.filter(customer=customer_obj),
			'users':WithdrawRequest.objects.all(), 'vendors':WithdrawRequest.objects.all(), 'categories':ProductCategory.objects.all(),
			'tds_wallet':TDSLogWallet.objects.filter(customer=customer_obj).first(),
            # 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/tdslog.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


##########################################################################################################################

from django.contrib.auth.decorators import login_required
from main_app.models import *
import random

from django.db import transaction


login_required('/')
@csrf_exempt
def wallet_transfer_vendor(request):

	if not Wallet.objects.filter(user=request.user).exists():
		Wallet.objects.create(user=request.user,current_balance=0)	
		
	try:
		bal = Wallet.objects.filter(user=request.user).first().current_balance
	except Wallet.DoesNotExist:
		user = None	
	
		

	vandordata = Vendor.objects.filter(is_active = True)
	transectiondata = WalletTransfer.objects.filter(user=request.user).order_by('-transection_time')
    
	context = {
			'vendordata': vandordata,
			'transectiodetails':transectiondata,
			'bal':bal,# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}

	user=WalletTransferApproval.objects.all()[0:1]
	print(user)

	if WalletTransferApproval.objects.get(id =user).customer == 1:
		if request.method == 'POST':
			request.session['recivername'] = request.POST.get('rvname') 
			request.session['amount']  = int(request.POST.get('amt'))
			request.session['senderotp'] = random.randint(100000,999999)
			# request.session['reciverotp'] = random.randint(100000,999999)
			request.session['type012'] = 1
			# request.session['timer'] = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
			# print('-------------------------->',request.session['timer'],type(request.session['timer']),request.session['type012'])
			print(request.session['senderotp'],'\n---------->',request.session['recivername'])
			msg = ''' Hi there!
Your OTP for wallet transfer for sending ₹''' + str(request.session['amount']) +''' to ''' + request.session['recivername']+ '''is ''' + str(request.session['senderotp'])+'''.

Thanks!'''
			EmailMessage('AVPL - OTP for Wallet transfer', msg, to=[request.user.email]).send()
			print(request.user.email)
			notification(request.user, 'OTP sent successfully.')
			messages.success(request, 'OTP sent successfully.')
			return render(request,'user_app/otpverify.html')
		

		return render(request,'user_app/vendorwallettransfer.html',context=context)

	else:
		messages.error(request,'Payments Mode off')
		return render(request,'user_app/vendorwallettransfer.html',context=context)


login_required('/')
@transaction.atomic
@csrf_exempt
def transfer_amount(request):
	
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
	
		# if datetime.datetime.now() < datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f') :
		
		if senderotp == request.session['senderotp']:
			
			if Wallet.objects.get(user=request.user).current_balance >= request.session['amount']:

				make_wallet_transaction(user = request.user, amount = request.session['amount'], trans_type = 'DEBIT')
				make_wallet_transaction(user = User.objects.get(username = request.session['recivername']), 
					amount = request.session['amount'], trans_type = 'CREDIT')
				print(request.session['recivername'])
				transfer_into_another_account(usr = request.user, sender = request.user.username,
					reciver = request.session['recivername'],amount = request.session['amount'])
				print('done!')
				user = User.objects.get(username = request.session['recivername'])
				notification(user, 'Money Successfully Recived.')
				notification(request.user, 'Money Successfully Transfered')
			
				messages.success(request,'Successfully Transfered')
				# if int(request.session['type012']) == 0:
				# 	return redirect('transfer_money')
				# else:
				return redirect('vendor-wallet-transfer')


			else :
				messages.error(request,'Not having sufficient balance')
				if int(request.session['type012']) == 0:
					return redirect('transfer_money')
				else:
					return redirect('vendor-wallet-transfer')

		else :
			messages.error(request,'OTP is not Correct ,Please enter correct OTP !')
			if int(request.session['type012']) == 0:
				return redirect('transfer_money')
			else:
				return redirect('otp-verification')
		# else:
		# 	messages.error(request,'Timeout')
		# 	if int(request.session['type012']) == 0:
		# 		return redirect('transfer_money')
		# 	else:
		# 		return redirect('transfer_money_vander')
	if int(request.session['type012']) == 0:
		return redirect('transfer_money')
	else:
		# return redirect('otp-verification')
		return render(request,'user_app/otpverify.html')



@csrf_exempt
@login_required(login_url='/login/')
def user_profile(request):
	if check_user_authentication(request, 'CUSTOMER'):
     
		customerobj=Customer.objects.filter(user=request.user).first()
		
		dic = {
		    "customer":customerobj,
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}			
		return render(request,'user_app/user-profile.html', dic)
	else:
		return render(request, '403.html')



@csrf_exempt
def edit_customer_profile(request):
	if check_user_authentication(request, 'CUSTOMER'):
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
   
			gstno=request.POST.get('gstno')
			gstnodoc = request.FILES.get('gstnodoc')

		
				
			
			print(mobile,'Mobile')
    
			
		
			customer_obj=Customer.objects.filter(user=request.user).first()
			
			user=User.objects.filter(id=request.user.id).first()
	
			if mobile:
				customer_obj.mobile = mobile
				user.username=mobile
			if email:
				user.email=email
			if firstname:
				customer_obj.firstname= firstname
				user.first_name=firstname
			if lastname:
				customer_obj.lastname= lastname
				user.last_name=lastname
			if gender:
				customer_obj.gender =  gender
			if dob:
				customer_obj.dob= dob
			if streetaddress:
				customer_obj.streetaddress =  streetaddress
			if nearbyaddress:
				customer_obj.nearbyaddress =  nearbyaddress
			if pincode:
				customer_obj.pincode = pincode
			if city:
				customer_obj.city= city
			if state:
				customer_obj.state= state
			if country:
				customer_obj.country= country
			if latitude:
				customer_obj.latitude =  latitude
			if longitude:
				customer_obj.longitude =  longitude
			if profilepic:
				customer_obj.profilepic =profilepic

			#Personal User 
			if pancardno:
				customer_obj.pancardno=pancardno
			if pancarddoc:
				customer_obj.pancarddoc =pancarddoc
			if idproof:
				customer_obj.idproof= idproof
			if idno:
				customer_obj.idno= idno
			if frontidproofdoc:
				customer_obj.frontidproofdoc =frontidproofdoc
			if backidproofdoc:
				customer_obj.backidproofdoc=backidproofdoc
			if addressproof:
				customer_obj.addressproof= addressproof
			if addressno:
				customer_obj.addressno= addressno
			if frontaddressproofdoc:
				customer_obj.frontaddressproofdoc =frontaddressproofdoc
			if backddressproofdoc:
				customer_obj.backddressproofdoc =backddressproofdoc
			
			if gstno:
				customer_obj.gstno=gstno
			if gstnodoc:
				customer_obj.gstnodoc = gstnodoc

   
			user.save()

			customer_obj.save()


			
			
			messages.info(request, 'Your Profile has been updated !')

		return redirect("/user/profile")
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def creditedmoney_user_wallet(request):
	if check_user_authentication(request, 'CUSTOMER'):
		# if not CreditedMoney.objects.filter(user=request.user).exists():
		# 	CreditedMoney.objects.create(user=request.user)
		dic = {"customer_obj":Customer.objects.filter(user=request.user).first(),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/creditedmoney_wallet-dash.html', dic)
	else:
		return render(request, '403.html')

