from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from inventory_app.models import Product, ProductCategory, ProductImages, ProductSubCategory, ProductSubSubCategory
from xhtml2pdf import pisa
from django.db.models import *
from django.contrib.auth.models import User
import datetime
import uuid
import requests
from django.contrib import messages
from sales_app.models import SalesOrder, SalesOrderItems
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
import random
import string

def generate_order_number(id):
    prefix = f'ORD{id}'  # Prefix for the order number
    length = 8  # Length of the random part of the order number

    # Generate a random string of digits and uppercase letters
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    return f"{prefix}{random_part}"


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

def save_order_items(cartobj, order, customer, ordertype):
	order=SalesOrder.objects.filter(id=order.id).first()
	for x in cartobj["items"]:
		# tax = 0.0
		print(x,'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiit')
		admincommission = x["admincommission"]
		print('VVVVV____Commm---===>',admincommission)
		orderitemobj = SalesOrderItems()
		orderitemobj.store = x["store"]
		order.store=x["store"]
		order.save()
		orderitemobj.salesorder =order
		orderitemobj.productvariants = x["productvariants"]
		orderitemobj.quantity =x["quantity"]
		orderitemobj.price = x["price"]
		orderitemobj.tax = x["tax"]
		orderitemobj.total =  x["total"]
		orderitemobj.orderstatus ="Pending"
		orderitemobj.save()
	
		save_vendor_commission(x["store"], x["total"], admincommission, ordertype)
		if x["store"].vendor.isavplvendor == True :
			print('Vendor_Commission ==>>>>>')
			per_product_vendor_commission(x["store"],customer, x["total"], admincommission, ordertype)
		
		# if len(Tax.objects.all()) == 0:
		# 	Tax.objects.create(current_tax = tax)
		# else:
		# 	current_tax = Tax.objects.all()[0].current_tax + tax
		# 	Tax.objects.all().update(current_tax = current_tax)
		
		productvariants=x["productvariants"]
		productvariants.quantity =productvariants.quantity - x["quantity"]
		productvariants.save()
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
def create_cod_order(cartobj, address,usertype, user):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
		# check_user_subscription(cart.user)
		total_amount=cartobj['total_amount']
		tax_amount=cartobj['tax_amount']
		subtotal_amount=cartobj['subtotal_amount']
		
		# if cart.self_pickup:
		# 	total = cart.total - cart.delivery_charges

		order = SalesOrder.objects.create(
			customer = customer,
			address = address,
			subtotal = subtotal_amount,
			tax = tax_amount,
			total = total_amount,
            
			# selfpickup = True
		)
		if order:
			order.orderno=generate_order_number(order.id)
			order.save()
		save_order_items(cartobj, order, customer, 'COD')

		Cart.objects.filter(customer=customer).delete()
		
# In case Online Payment
def save_order(cartobj, address,usertype, user, razorpaytransaction):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
		total_amount=cartobj['total_amount']
		tax_amount=cartobj['tax_amount']
		subtotal_amount=cartobj['subtotal_amount']
	print(razorpaytransaction)
	paymenttransactionobj=PaymentTransaction.objects.filter(transactionid=razorpaytransaction).first()
	if paymenttransactionobj.status == True:
		ispaymentpaid=True
	else:
		ispaymentpaid=False
	order = SalesOrder.objects.create(
		customer = customer,
		address = address,
		subtotal = subtotal_amount,
		tax = tax_amount,
		total = total_amount,
        ispaymentpaid=ispaymentpaid,
		paymenttransaction=paymenttransactionobj,
		
		# selfpickup = True
	)
	if order:
		order.orderno=generate_order_number(order.id)
		order.save()
	save_order_items(cartobj, order, customer, 'Online')

	Cart.objects.filter(customer=customer).delete()
 

   
# In case make  Payment by wllet
def make_wallet_transaction(usertype, user, amount, transtype):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
		if not Wallet.objects.filter(customer=customer).exists():
			wallet=Wallet.objects.create(customer=customer,isactive=True)
		else:
			wallet = Wallet.objects.filter(customer=customer,isactive=True).first()
      
	elif usertype == "VENDOR":
		vendor=Vendor.objects.filter(user=user).first()
		if not Wallet.objects.filter(vendor=vendor).exists():
			wallet=Wallet.objects.create(vendor=vendor,isactive=True)
		else:
			wallet = Wallet.objects.filter(vendor=vendor,isactive=True).first()
	elif usertype == "ADMIN":
		admin=user
		if not Wallet.objects.filter(admin=admin).exists():
			wallet=Wallet.objects.create(admin=admin,isactive=True)
		else:
			wallet = Wallet.objects.filter(admin=admin,isactive=True).first()
   
	if transtype == 'CREDIT':
		print('1')
		wallettransactions = WalletTransaction.objects.create(
			wallet = wallet,
			transactiondate = timezone.now(),
			transactiontype = transtype,
			transactionamount = amount,
			previousamount = round(wallet.currentbalance, 2),
			remainingamount = round(wallet.currentbalance,2) + round(amount,2)
		)
		wallet.currentbalance = round(wallet.currentbalance, 2) + round(amount, 2)
		wallet.save()

	elif transtype == 'DEBIT':
		print(2)
		wallettransactions = WalletTransaction.objects.create(
			wallet = wallet,
			transactiondate = timezone.now(),
			transactiontype = transtype,
			transactionamount = amount,
			previousamount = round(wallet.currentbalance, 2),
			remainingamount = round(wallet.currentbalance, 2) - round(amount,2)
		)
		wallet.currentbalance = round(wallet.currentbalance, 2) - round(amount, 2)
		wallet.save()


def save_order_by_wallet(cartobj, address,usertype, user, wallet_transactions):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
		total_amount=cartobj['total_amount']
		tax_amount=cartobj['tax_amount']
		subtotal_amount=cartobj['subtotal_amount']
	print(wallet_transactions)
  
	paymenttransactionobj=PaymentTransaction()
	paymenttransactionobj.customer = customer
	paymenttransactionobj.paymentgatway='Wallet'
	paymenttransactionobj.transactionid =wallet_transactions.id
	paymenttransactionobj.transactionrealted= 'PRODUCT-ORDER'
	paymenttransactionobj.transactiondetails = wallet_transactions.id
	paymenttransactionobj.amount = wallet_transactions.transactionamount
	paymenttransactionobj.address = address
	paymenttransactionobj.status = True
	paymenttransactionobj.save()

	order = SalesOrder.objects.create(
		customer = customer,
		address = address,
		subtotal = subtotal_amount,
		tax = tax_amount,
		total = total_amount,
		paymenttransaction=paymenttransactionobj,
		ispaymentpaid=True,
		# selfpickup = True
	)
	if order:
		order.orderno=generate_order_number(order.id)
		order.save()
	save_order_items(cartobj, order, customer, 'Online')

	Cart.objects.filter(customer=customer).delete()
    
	print(wallet_transactions)
	

def save_vendor_commission(store, amount, percentage, ordertype = 'COD'):
	if ordertype == 'Online':
		admin_commission = (amount/100)*percentage
		remaining_amount = amount - admin_commission
		# Credited amount to vendor wallet
		make_wallet_transaction("VENDOR",store.vendor.user, remaining_amount, 'CREDIT')
		# Credited amount to admin commission wallet
		admin=User.objects.filter(username="admin").first()
		make_commission_transaction("ADMIN", admin, admin_commission, 'CREDIT')
		# if UserVendorRelation.objects.filter(vendor__id=user.id).exists():
		# 	user__ = UserVendorRelation.objects.filter(vendor=user.id)
		# 	#user commission 10% of vendor amount
		# 	user_c = (remaining_amount * 10)/100
		# 	# credit amount 10% in user wallet
		# 	make_wallet_transaction(user__.user, user_c, 'CREDIT')
		# 	print(user.first_name+"Vendor paid User Commission to ")
		return admin_commission
	else:
		admin_commission = (amount/100)*percentage
		return admin_commission

def make_commission_transaction(usertype,user, amount, transtype):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
		if not CommissionWallet.objects.filter(customer=customer).exists():
			commissionwallet=CommissionWallet.objects.create(customer=customer,isactive=True)
		else:
			commissionwallet = CommissionWallet.objects.filter(customer=customer,isactive=True).first()
		
	elif usertype == "VENDOR":
		vendor=Vendor.objects.filter(user=user).first()
		if not CommissionWallet.objects.filter(vendor=vendor).exists():
			commissionwallet=CommissionWallet.objects.create(vendor=vendor,isactive=True)
		else:
			commissionwallet = CommissionWallet.objects.filter(vendor=vendor,isactive=True).first()
	elif usertype == "ADMIN":
		admin=user
		if not CommissionWallet.objects.filter(admin=admin).exists():
			commissionwallet=CommissionWallet.objects.create(admin=admin,isactive=True)
		else:
			commissionwallet = CommissionWallet.objects.filter(admin=admin,isactive=True).first()

	if transtype == 'CREDIT':
		CommissionWalletTransaction.objects.create(
            commissionwallet = commissionwallet,
			transactiondate = timezone.now(),
			transactiontype = transtype,
			transactionamount = amount,
			previousamount = round(commissionwallet.currentbalance, 2), 
			remainingamount = round((commissionwallet.currentbalance + amount),2) 
		)
		commissionwallet.currentbalance=round((commissionwallet.currentbalance + amount),2)
		commissionwallet.save()
  
	elif transtype == 'DEBIT':
		CommissionWalletTransaction.objects.create(
            commissionwallet = commissionwallet,
			transactiondate = timezone.now(),
			transactiontype = transtype,
			transactionamount = amount,
            previousamount = round(commissionwallet.currentbalance, 2), 
			remainingamount = round((commissionwallet.currentbalance - amount),2) 
		)
		commissionwallet.currentbalance=round((commissionwallet.currentbalance - amount),2)
		commissionwallet.save()

def per_product_vendor_commission(store,customer, amount, percentage, ordertype = 'COD'):
	if ordertype == 'Online':
		vendor_commission = (amount/100)*percentage
		remaining_amount = amount - vendor_commission
		# Credited amount to vendor wallet
		# make_wallet_transaction(vendor, remaining_amount, 'CREDIT')
			# Credited amount to admin commission wallet
		make_commission_transaction("VENDOR",store.vendor.user, vendor_commission, 'CREDIT')
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

def make_business_limit_transaction(usertype,user, amount, trans_type, trans_name):
	if usertype == 'VENDOR' :
		vendor=Vendor.objects.filter(user=user).first()
	if not BusinessLimitWallet.objects.filter(vendor=vendor).exists():
		BusinessLimitWallet.objects.create(vendor=vendor)
	business_limit = BusinessLimitWallet.objects.get(vendor=vendor)
	if trans_type == 'CREDIT':
		BusinessLimitWalletTransaction.objects.create(
		businesslimitwallet = business_limit,
		transactiondate = timezone.now(),
		transactiontype = trans_type,
		transactionamount = amount,
		previousamount = business_limit.currentbalance,
		remainingamount = business_limit.currentbalance + amount

		)
		BusinessLimitWallet.objects.filter(vendor=vendor).update(currentbalance = business_limit.currentbalance + amount)
	if trans_type == 'DEBIT':
		print(amount)
		remaining_amount = business_limit.currentbalance - amount
		BusinessLimitWalletTransaction.objects.create(
			businesslimitwallet = business_limit,
			transactiondate = timezone.now(),
			transactiontype = trans_type,
			transactionamount = amount,
			previousamount = business_limit.currentbalance,
			remainingamount = remaining_amount
		)
		BusinessLimitWallet.objects.filter(vendor=vendor).update(currentbalance = remaining_amount)

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
	data = WalletBalanceTransfer(sender=sender, receiver = reciver, transectionid =td, amount=amount)
	if xval == 10000:
		xval = 1
	try :
		data.save()
	except :
		transfer_into_another_account(usr,sender,reciver,amount)
