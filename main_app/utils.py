from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from inventory_app.models import Product, ProductImages
from xhtml2pdf import pisa
from django.db.models import *
from django.contrib.auth.models import User
import datetime
import uuid
import requests
from django.contrib import messages
from user_app.utils import get_wishlist_len
from vendor_app.models import *
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from user_app.models import *
from user_app.utils import *
from admin_app.models import *
from django.utils import timezone
from .models import *
import datetime
import timeago

def generate_link(user,for_,type_):

	# id_ = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user.id)  +str(datetime.date.today())))

	id_ = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user.id)+str(type_)))
	
	
	
	if for_ == 'Admin':
	
		link = 'http://127.0.0.1:8000/?u='+id_+'&t=a'
		if not UserLinkType.objects.filter(user=user,link_type=type_,link=link).exists():
		   UserLinkType.objects.create(user=user,link_type=type_,link=link,links=id_)
		   

	elif for_ == 'User':
		
		link = 'http://127.0.0.1:8000/?u='+id_+'&t=u'
		if not UserLinkType.objects.filter(user=user,link_type=type_,link=link).exists():
		   UserLinkType.objects.create(user=user,link_type=type_,link=link,links=id_)
		   

	elif for_ == 'Vendor':
		
		link = 'http://127.0.0.1:8000/?u='+id_+'&t=v'
		if not UserLinkType.objects.filter(user=user,link_type=type_,link=link).exists():
			UserLinkType.objects.create(user=user,link_type=type_,link=link,links=id_)

	return link

	

def get_user_from_key(key,type_):
	for x in User.objects.all():
		# u = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(x.id)  +str(datetime.date.today())))
		
		u = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(x.id)+str(type_)))

		print(u,key)

	
		if u == key:
			return x
	return False

def get_store_rating(store):
	initial_rating = 0.0
	l = 0
	for product in Product.objects.filter(store=store):
		print(product)
		for rating in ProductRating.objects.filter(product=product):
			rating = rating.rating
			rating = int(rating)
			print(rating)
			rating = initial_rating + rating
			l = l + 1
			if rating > 0.0:
				average = rating/l
				return round(average, 1)
			else:
				return rating

#function for subsubcategory wise stores
def fetch_vendors_subsubcatby(subsubcategory,lat, lng):
	res = []
	for y in Product.objects.filter(subsubcategory=subsubcategory):
		res.append(y.store)
	results=[]
	for i in fetch_vendors(lat, lng):
		if i['store'].store in res:
			results.append(i)
	return results

#function for subcategory wise stores
def fetch_vendors_subcatby(subcategory,lat, lng):
	res = []
	for y in Product.objects.filter(subcategory=subcategory):
		res.append(y.store)
	results=[]
	for i in fetch_vendors(lat, lng):
		if i['store'].store in res:
			results.append(i)
	return results

#function for category wise stores
def fetch_vendors_catby(category,lat, lng):
	#stores = fetch_vendors(lat, lng)
	res = []
	for y in Product.objects.filter(category=category):
		res.append(y.store)
	results=[]
	for i in fetch_vendors(lat, lng):
		if i['store'].id in res:
			results.append(i)
	return results

def fetch_vendors(lat, lng):
	results = []
	newport_ri = (lat, lng)
	for x in Vendor.objects.all():
		# print(x.store_latitude,x.store_longitude)
		cleveland_oh = (x.latitude, x.longitude)
		c = geodesic(newport_ri, cleveland_oh).miles
		Km = c / 0.62137
		if Km <= 10:
			results.append({
				'store':x,
				'distance':round(Km, 4),
				'price':ProductVariants.objects.filter(store__vendor__id=x.id).order_by('price'),
				# 'rating':get_store_rating(x.store)
			})
	return results

def get_store_distance(lat, lng, lat_vendor, lng_vendor):
	newport_ri = (lat, lng)
	cleveland_oh = (lat_vendor, lng_vendor)
	c = geodesic(newport_ri, cleveland_oh).miles
	Km = c / 0.62137
	return Km

def getproduct_bylocation(lat, lng):
	vendors = fetch_vendors(lat, lng)
	products = []
	for v in vendors:
		vendor = v['store']
		if Store.objects.filter(vendor=vendor).exists():
			for product in Product.objects.filter(store__vendor__id=vendor.id, isactive=True):
				products.append(product)
	return products

def get_store_categories(store, lat, lng):
	products = getproduct_bylocation(lat, lng)
	categories = []
	for x in products:
		if x.store == store:
			categories.append(x.category)
	return categories

def get_dic(request):
	dic = {
		'categories':ProductCategory.objects.all(),
		'subcategories':ProductSubCategory.objects.all(),
		'subsubcategories':ProductSubSubCategory.objects.all(),
		'lat':False,
		'lng':False
	}
	if request.user.is_authenticated:
		#print(request.user.role.level.level)
		if check_user_authentication(request, 'CUSTOMER'):
			user = Customer.objects.get(user=request.user)
			request.session['lat'] = user.latitude
			request.session['lng'] = user.longitude
			dic.update({'lat':user.latitude, 'lng':user.longitude})
	dic.update(get_cart_len(request, 'CUSTOMER'))
	dic.update(get_wishlist_len(request, 'CUSTOMER'))
	return dic

def save_order_items(cart, order, user, ordertype = 'COD', plan = 'Binary'):
	cartitems = CartItems.objects.filter(cart=cart)
	print(plan)
	print(user,'USERSSSSSSSSS')
	for x in cartitems:
		tax = (x.total_cost/100)*x.product.category.tax
		# tax = 0.0
		vendor_commission = x.product.vendor_commission
		print('VVVVV____Commm---===>',vendor_commission)
		orderitem = OrderItems.objects.create(
			store = x.product.store,
			order = order,
			product = x.product,
			quantity = x.quantity,
			per_item_cost = x.per_item_cost,
			subtotal = x.total_cost,
			tax = tax,
			total = x.total_cost + tax,
			plan = plan
		)
		save_vendor_commission(x.product.store.vendor.user, x.total_cost + tax, x.product.category.commission, ordertype)
		if x.product.store.vendor.is_AVPL_Vendor == True :
			print('Vendor_Commission ==>>>>>')
			per_product_vendor_commission(x.product.store.vendor.user,user, x.total_cost + tax, x.product.vendor_commission, ordertype)

		
		if len(Tax.objects.all()) == 0:
			Tax.objects.create(current_tax = tax)
		else:
			current_tax = Tax.objects.all()[0].current_tax + tax
			Tax.objects.all().update(current_tax = current_tax)
		
		for y in CartItemVariant.objects.filter(cartitem=x):
			OrderItemVariant.objects.create(order=order, orderitem=orderitem, product_variant=y.product_variant)
			pro_var = ProductVariant.objects.get(product=x.product, variant=y.product_variant.variant, variant_value=y.product_variant.variant_value)
			variant_stock = (pro_var.variant_stock-x.quantity)
			if variant_stock < 0:
				variant_stock = 0
			ProductVariant.objects.filter(product=x.product, variant=pro_var.variant, variant_value=pro_var.variant_value).update(
				variant_stock=variant_stock
			)
		Product.objects.filter(id=x.product.id).update(stock=x.product.stock-x.quantity)
		# save_pv_transaction(user, x.product, x.total_cost, plan)

def binary_mlm(user, pv):
	if user.role.level.level == 'User':
		mlm = MLM.objects.get(node=user)
		if not mlm.parent.is_superuser:
			if not UserPV.objects.filter(user=mlm.parent).exists():
				UserPV.objects.create(user=mlm.parent)
			parent_pv = UserPV.objects.get(user=mlm.parent)
			if mlm.parent.email != 'admin@avpl.com':
				nodes = fetch_nodes(mlm.parent)
				for node in nodes['left']:
					if node == user:
						UserPV.objects.filter(user=mlm.parent).update(left_pv=(parent_pv.left_pv+pv))
						break
				for node in nodes['right']:
					if node == user:
						UserPV.objects.filter(user=mlm.parent).update(right_pv=(parent_pv.right_pv+pv))
						break
				binary_mlm(mlm.parent, pv)

def level_mlm(user, pv):
	parents = fetch_parent_nodes(user, [])
	# print(len(parents),'LLLLLL')
	# parentss = Level_Plan_Referrals.objects.filter(referrals=user).first()
	# print(parentss.level_plan_referral,'YYYYYYYYYYYYYYY')
	# parents=parentss.level_plan_referral
	if parents is not None:
		if len(parents)  > 0:
			count = 0
			levels = Level_Settings.objects.all()[0]

			level_groups=Level_Group.objects.filter(level=levels)

			print(level_groups,'level_group--------')

			for group in level_groups:
				for x in range(1, group.no_of_levels+1):
					count = count + x
					new_pv = (pv/100)*group.percent_per_level
					if len(parents) >= count:
						userpv = UserPV.objects.get(user=parents[count-1])
						userpv.level_pv = userpv.level_pv + new_pv
						userpv.save()
					else:
						break
			new_pv = (pv/100)*20
			userpv = UserPV.objects.get(user=user)
			userpv.level_pv = userpv.level_pv + new_pv
			userpv.save()
		else:
			new_pv = (pv/100)*20
			userpv = UserPV.objects.get(user=user)
			userpv.level_pv = userpv.level_pv + new_pv
			userpv.save()
	else:
		print('parents has none  value')

def update_user_pv(user, pv, plan):
	if plan == 'Binary':
		binary_mlm(user, pv)
	elif plan == 'Level':
		level_mlm(user, pv)

def save_pv_transaction(user, product, subtotal, plan):
	pv_percent = PointValue.objects.get(category=product.category).percentage
	print(pv_percent,'ggggggg')
	print(plan,'fffff')
	print(user)
	pv = (subtotal/100)*pv_percent
	print(pv,'hhhhhhh')
	total_pv = user.usr.pv + pv
	print(total_pv,'lllllll')
	PVTransactions.objects.create(
		user = user,
		transaction_date = timezone.now(),
		previous_pv = user.usr.pv,
		pv = pv,
		total_pv = user.usr.pv + pv,
		plan = plan
	)
	update_user_pv(user, pv, plan)
	UserData.objects.filter(user=user).update(pv=total_pv)

def getresult(key, category, brand, min_price, max_price, in_stock, rate):
	if Product.objects.filter(isactive = True):
		if category != '0' and key =='' and brand is None:
			print('1')
			return Product.objects.filter(category__id=category , isactive=True)
		if brand and category == '' and key =='' :
			print('6')
			return Product.objects.filter(brand__id=brand , isactive=True)
		elif key and category=='0' and brand is None:
			print('2')
			return Product.objects.filter(Q(name__icontains=key) , Q(description__icontains=key),isactive=True)
		elif category and key:
			print('3')
			key_prod = Product.objects.filter(Q(name__icontains=key , isactive=True) )
			cat_prod = key_prod.filter(category__id=category)
			return cat_prod
		elif category is None and key is None and brand is None and max_price and min_price and in_stock is None:
			print('5')
			return Product.objects.filter(price__range = [min_price,max_price] , isactive=True)
		elif category is None and key is None and brand is None and max_price and min_price and in_stock:
			print('8')
			for i in Product.objects.all():
				if i.stock >= 1 :
					return Product.objects.filter(price__range = [min_price,max_price] , isactive=True)
		elif rate and category is None and key is None and brand is None and max_price is None and min_price is None and in_stock  is None:
			product = ProductRating.objects.filter(rating = float(rate) ).values().first()
			if product:
				return Product.objects.filter(id = product['product_id'])
			else:
				messages.warning(requests,f'No product with this rating')
				return Product.objects.all()
		else:
			print('4')
			return Product.objects.filter(isactive=True)




import random

def get_product_thumb(product):
	productvariantsobj=ProductVariants.objects.filter(product=product).first()
	if productvariantsobj:
		dic = {'product':product, 'image':productvariantsobj.productimage}
		ratings = ProductRating.objects.filter(productvariants=productvariantsobj)
		total = 0.0
		for x in ratings:
			total = total + x.rating
		rating = 0.0
		if len(ratings) <= 0:
			rating = 0.0
		else:
			rating = (total/len(ratings))
		dic.update({'rating':round(rating, 1)})
		fake_price = (productvariantsobj.price/100)*50
		dic.update({'rating':round(rating, 1), 'fake_price':round(fake_price+productvariantsobj.price, 2)})
		pv_percent = product.pv
		pv = (productvariantsobj.price/100)*pv_percent
		dic.update({'pv':round(pv, 1)})
	else:
		dic = {'product':None, 'image':None,rating:None,fake_price:None,pv:None}
	return dic

# In case Case on delivey
def create_cod_order(cart, address, user, plan):
	cartitems = CartItems.objects.filter(cart=cart)
	check_user_subscription(cart.user)
	if cart.self_pickup:
		total = cart.total - cart.delivery_charges
		order = Orders.objects.create(
			order_date = timezone.now(),
			user = user,
			address = address,
			subtotal = cart.subtotal,
			tax = cart.tax,
			total = total,
			point_value = calculate_point_value_on_order(cart),
			self_pickup = True
		)
		save_order_items(cart, order, user, 'COD', plan)
		Cart.objects.filter(id=cart.id).delete()
	else:
		if user.usr.subscribed and (cart.total >= Min_Amount_For_Free_Delivery.objects.all()[0].amount):
			total = cart.total - cart.delivery_charges
		order = Orders.objects.create(
			order_date = timezone.now(),
			user = user,
			address = address,
			delivery_charges = cart.delivery_charges,
			subtotal = cart.subtotal,
			tax = cart.tax,
			total = cart.total,
			point_value = calculate_point_value_on_order(cart),
		)
		save_order_items(cart, order, user, 'COD', plan)
		Cart.objects.filter(id=cart.id).delete()

# In case Online Payment
def save_order(cart, address, user, razorpaytransaction):
	print(razorpaytransaction)
	cartitems = CartItems.objects.filter(cart=cart)
	if cart.self_pickup:
		total = cart.total - cart.delivery_charges
		order = Orders.objects.create(
			order_date = timezone.now(),
			user = user,
			razorpaytransaction = razorpaytransaction,
			address = address,
			subtotal = cart.subtotal,
			tax = cart.tax,
			total = total,
			point_value = calculate_point_value_on_order(cart),
			self_pickup = True,
			paid = True
		)
		save_order_items(cart, order, user, 'Online')
		Cart.objects.filter(id=cart.id).delete()
	else:
		order = Orders.objects.create(
			order_date = timezone.now(),
			user = user,
			razorpaytransaction = razorpaytransaction,
			address = address,
			delivery_charges = cart.delivery_charges,
			subtotal = cart.subtotal,
			tax = cart.tax,
			total = cart.total,
			point_value = calculate_point_value_on_order(cart),
			paid = True
		)
		save_order_items(cart, order, user, 'Online')
		Cart.objects.filter(id=cart.id).delete()


# In case make  Payment by wllet
def make_wallet_transaction(user, amount, trans_type):
	if not Wallet.objects.filter(user=user).exists():
		Wallet.objects.create(user=user)
	wallet = Wallet.objects.filter(user=user).first()
	print(wallet)
	if trans_type == 'CREDIT':
		print('1')
		wallet_transactions = WalletTransaction.objects.create(
			wallet = wallet,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			previous_amount = round(wallet.current_balance, 2),
			remaining_amount = round(wallet.current_balance,2) + round(amount,2)
		)
		Wallet.objects.filter(user=user).update(current_balance = round(wallet.current_balance, 2) + round(amount, 2))


	elif trans_type == 'DEBIT':
		print(2)
		wallet_transactions = WalletTransaction.objects.create(
			wallet = wallet,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			previous_amount = wallet.current_balance,
			remaining_amount = wallet.current_balance - amount
		)
		print(wallet)
		Wallet.objects.filter(user=user).update(current_balance = wallet.current_balance - amount)

	

def save_order_by_wallet(cart, address, user, wallet_transactions):
	print(wallet_transactions)
	cartitems = CartItems.objects.filter(cart=cart)
	if cart.self_pickup:
		total = cart.total - cart.delivery_charges
		order = Orders.objects.create(
			order_date = timezone.now(),
			user = user,
			wallet_transactions = wallet_transactions,
			address = address,
			subtotal = cart.subtotal,
			tax = cart.tax,
			total = total,
			point_value = calculate_point_value_on_order(cart),
			self_pickup = True,
			paid = True
		)
		save_order_items(cart, order, user, 'Online')
		Cart.objects.filter(id=cart.id).delete()
	else:
		order = Orders.objects.create(
			order_date = timezone.now(),
			user = user,
			wallet_transactions = wallet_transactions,
			address = address,
			delivery_charges = cart.delivery_charges,
			subtotal = cart.subtotal,
			tax = cart.tax,
			total = cart.total,
			point_value = calculate_point_value_on_order(cart),
			paid = True
		)
		save_order_items(cart, order, user, 'Online')
		Cart.objects.filter(id=cart.id).delete()



def save_vendor_commission(user, amount, percentage, ordertype = 'COD'):
	if ordertype == 'Online':
		admin_commission = (amount/100)*percentage
		remaining_amount = amount - admin_commission
		# Credited amount to vendor wallet
		make_wallet_transaction(user, remaining_amount, 'CREDIT')
		# Credited amount to admin commission wallet
		make_commission_transaction(user, admin_commission, 'CREDIT')
		if UserVendorRelation.objects.filter(vendor__id=user.id).exists():
			user__ = UserVendorRelation.objects.filter(vendor=user.id)
			#user commission 10% of vendor amount
			user_c = (remaining_amount * 10)/100
			# credit amount 10% in user wallet
			make_wallet_transaction(user__.user, user_c, 'CREDIT')
			print(user.first_name+"Vendor paid User Commission to ")
		return admin_commission
	else:
		admin_commission = (amount/100)*percentage
		return admin_commission

def make_commission_transaction(user, amount, trans_type):
	if len(Commission.objects.all()) == 0:
		Commission.objects.create()
	commission = Commission.objects.all()[0]
	print(commission,'LLLLLLLLLL')
	if trans_type == 'CREDIT':
		CommissionTransaction.objects.create(
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			user = user,
			previous_amount = commission.current_balance,
			remaining_amount = commission.current_balance + amount
		)
		Commission.objects.all().update(current_balance=commission.current_balance + amount)
	elif trans_type == 'DEBIT':
		CommissionTransaction.objects.create(
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			user = user,
			previous_amount = commission.current_balance,
			remaining_amount = commission.current_balance - amount
		)
		Commission.objects.all().update(current_balance=commission.current_balance - amount)

def per_product_vendor_commission(vendor,user, amount, percentage, ordertype = 'COD'):
	if ordertype == 'Online':
		vendor_commission = (amount/100)*percentage
		remaining_amount = amount - vendor_commission
		# Credited amount to vendor wallet
		# make_wallet_transaction(vendor, remaining_amount, 'CREDIT')
			# Credited amount to admin commission wallet
		make_vendor_commission_transaction(vendor,user, vendor_commission, 'CREDIT')
		# if UserVendorRelation.objects.filter(vendor__id=vendor.id).exists():
		# 	user__ = UserVendorRelation.objects.filter(vendor=user.id)
		# 	#user commission 10% of vendor amount
		# 	user_c = (remaining_amount * 10)/100
		# 	# credit amount 10% in user wallet
		# 	make_wallet_transaction(user__.user, user_c, 'CREDIT')
		# 	print(user.first_name+"Vendor paid User Commission to ")
		return vendor_commission
	else:
		vendor_commission = (amount/100)*percentage
		return vendor_commission

def make_vendor_commission_transaction(vendor,user, amount, trans_type):
	if not Vendor_Wallet_Commission.objects.filter(user=vendor).exists():
		Vendor_Wallet_Commission.objects.create(user=vendor)
	wallet_commission = Vendor_Wallet_Commission.objects.get(user=vendor)
	if trans_type == 'CREDIT':
		VendorWalletTransaction.objects.create(
			vendor_wallet_commission = wallet_commission,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			user = user,
			previous_amount = wallet_commission.current_balance,
			remaining_amount = wallet_commission.current_balance + amount
		)
		Vendor_Wallet_Commission.objects.filter(user=vendor).update(current_balance=wallet_commission.current_balance + amount)
	elif trans_type == 'DEBIT':
		VendorWalletTransaction.objects.create(
			vendor_wallet_commission = wallet_commission,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			user = user,
			previous_amount = Vendor_Wallet_Commission.current_balance,
			remaining_amount = Vendor_Wallet_Commission.current_balance - amount
		)
		Vendor_Wallet_Commission.objects.filter(user=vendor).update(current_balance=Vendor_Wallet_Commission.current_balance - amount)

def sort_products(products, flag):
	if flag == 3:
		products = list(reversed(products))
		return products
	prize = []
	results = []
	for p in products:
		prize.append(p['product'].price)

	if flag == 1:
		prize.sort()

	elif flag == 2:
		prize.sort(reverse=True)

	prize = list(zip(prize))
	for x in prize:
		for y in products:
			if x[0] == y['product'].price:
				results.append(y)
	return results

def brand_filter(brands_ids, products):
	results = []
	for i in brands_ids:
		for x in Product.objects.filter(brand = Brand.objects.get(id = int(i))):
			for y in products:
				if y['product'].id == x.id:
					results.append(y)
	return results

def get_variants(products):
	lt = []
	for x in products:
		for y in ProductVariant.objects.filter(product=x['product']):
			dic = {'variant':y.variant, 'values':VariantValue.objects.filter(variant=y.variant)}
			lt.append(dic)
	lt2 = lt
	count = 0
	for x in lt:		
		for y in lt2:
			if x == y:
				count = count + 1
		if count > 1:
			lt.remove(x)
			count = 0
	return lt2

def variant_filter(variant_values, products):
	results = []
	if len(variant_values) > 0:
		for x in variant_values:
			for y in ProductVariant.objects.filter(variant_value=VariantValue.objects.get(id=int(x))):
				for z in products:
					if y.product == z['product']:
						results.append(z)
		lt = results
		count = 0
		for x in results:
			for y in lt:
				if x == y:
					count = count + 1
			if count > 1:
				results.remove(x)
				count = 0
		return results
	else:
		return products

def notification(user, text):
	Notification.objects.create(user=user, notification_date = datetime.datetime.now().replace(tzinfo=None), text=text)



def get_notifications(user,usertype):
	now_date = datetime.datetime.now() 
	if usertype == "ADMIN" :
		notifications = Notification.objects.filter(admin=user)
	elif usertype == "ADMIN-STAFF" :
		notifications = Notification.objects.filter(admin=user)
	elif usertype == "CUSTOMER" :
		notifications = Notification.objects.filter(customer__user=user)
	elif usertype == "VENDOR" :
		notifications = Notification.objects.filter(vendor__user=user)
	elif usertype == "VENDOR-STAFF" :
		notifications = Notification.objects.filter(admin=user)
	else:
		pass

	lt = [{
		'subject': x.subject,
		'message': x.message,
        'isread': x.isread,
        'isreadby': x.isreadby,
		'time': timeago.format(x.createdat, now_date, locale='en_short')
	} for x in notifications]
	return list(reversed(lt))



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def filter_product_by_store(store, products):
	results = []
	for x in products:
		if x['product'].store == store:
			results.append(x)
	return results

# for Admin comission transaction in case COD
from vendor_app.models import *
def make_business_limit_transaction(vendor, amount, trans_type, trans_name):
	if not BusinessLimit.objects.filter(vendor=vendor).exists():
		BusinessLimit.objects.create(vendor=vendor)
	business_limit = BusinessLimit.objects.get(vendor=vendor)
	if trans_type == 'CREDIT':
		BusinessLimitTransaction.objects.create(
		business_limit = business_limit,
		transaction_date = timezone.now(),
		transaction_type = trans_type,
		transaction_amount = amount,
		transaction_name =trans_name,
		previous_amount = business_limit.current_balance,
		remaining_amount = business_limit.current_balance + amount
		)
		BusinessLimit.objects.filter(vendor=vendor).update(current_balance = business_limit.current_balance + amount)
	if trans_type == 'DEBIT':
		print(amount)
		remaining_amount = business_limit.current_balance - amount
		BusinessLimitTransaction.objects.create(
			business_limit = business_limit,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			transaction_name =trans_name,
			previous_amount = business_limit.current_balance,
			remaining_amount = remaining_amount
		)
		BusinessLimit.objects.filter(vendor=vendor).update(current_balance = remaining_amount)

# save pv transaction for Subscription
def save_pv_transaction2(user, subtotal, plan):
	pv_percent = 10
	pv = (subtotal/100)*pv_percent
	PVTransactions.objects.create(
		user = user,
		transaction_date = timezone.now(),
		previous_pv = user.usr.pv,
		pv = pv,
		total_pv = user.usr.pv + pv,
		plan = plan
	)
	update_user_pv(user, pv, plan)
	#UserData.objects.filter(user=user).update(pv=total_pv)

def check_user_authentication(request, user_type):
	if request.user.is_authenticated:
		if request.user.groups.filter(name=user_type):
			return True
	return False

xval = 1
def transfer_into_another_account(usr,sender,reciver,amount):
	global xval
	td = str(sender[:2]).upper() + str(datetime.date.today()).replace('-','') + str(random.randint(1000,9999)) + str(xval)
	data = WalletTransfer(user=usr,senderusername=sender, reciverusername = reciver, transection_id =td, amount=amount)
	if xval == 10000:
		xval = 1
	try :
		data.save()
	except :
		transfer_into_another_account(usr,sender,reciver,amount)

