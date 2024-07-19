from datetime import timedelta
from user_app.models import *
from main_app.utils import *
from main_app.mlm_utils import *
from vendor_app.models import *
from django.utils import timezone

def get_cart_len(request,user_type):
	if user_type == "CUSTOMER":
		if Cart.objects.filter(customer__user=request.user).exists():
			cartobj = Cart.objects.filter(customer__user=request.user)
			cart_len=len(cartobj)
		else:
			cart_len = 0
	else:
		if Cart.objects.filter(vendor__user=request.user).exists():
			cartobj = Cart.objects.filter(vendor__user=request.user)
			cart_len=len(cartobj)
		else:
			cart_len = 0
	dic = {'cart_len':cart_len}
	return dic

def get_wishlist_len(request,user_type):
	if user_type == "CUSTOMER":
		if Wishlist.objects.filter(customer__user=request.user).exists():
			wishlistobj = Wishlist.objects.filter(customer__user=request.user)
			wish_len=len(wishlistobj)
		else:
			wish_len = 0
	else: 
		if Wishlist.objects.filter(vendor__user=request.user).exists():
			wishlistobj = Wishlist.objects.filter(vendor__user=request.user)
			wish_len=len(wishlistobj)
		else:
			wish_len = 0
	dic = {'wish_len':wish_len}
	return dic
	
def get_cart_items(request,user_type):
	if user_type == "CUSTOMER":
		cartobj = Cart.objects.filter(customer__user=request.user)
	else:
		cartobj = Cart.objects.filter(vendor__user=request.user)
	print(cartobj)

	# Initialize list and totals
	item_list = []
	total_amount = 0
	total_admincommission = 0
	tax_amount = 0
	subtotal_amount = 0

	# Iterate through cart items and create dictionaries
	for item in cartobj:
		price = item.productvariants.saleprice()
		admincommission=item.productvariants.admincommissionprice()
		perproducttax= round( (price) * ((item.productvariants.product.tax/100) / (1 + (item.productvariants.product.tax/100))),2)
		tax = round((perproducttax * item.quantity),2)
		total = round((price * item.quantity),2)
  
		item_dict = {
			'id': item.id,
            'store': item.productvariants.store,
			'image': item.productvariants.productimage.url,
			'name': item.productvariants.productvariantname,
			'quantity': item.quantity,
			'price': price,
			'mrp': item.productvariants.mrp,
			'tax': tax,
			'total': total,
            'pv':item.productvariants.product.pv,
            'admincommission':admincommission,
            'product':item.productvariants.product,
			'product_id': item.productvariants.id,
            'productvariants': item.productvariants,
			'stock_out': item.productvariants.quantity == 0
		}
		
		# Add the dictionary to the list
		item_list.append(item_dict)
		
		# Update totals
		tax_amount += tax
		subtotal_amount += round((total - tax_amount),2)
		total_admincommission += admincommission
		total_amount += total

	dic = {'items':item_list,'tax_amount':tax_amount,"total_admincommission":total_admincommission, "subtotal_amount":subtotal_amount,'total_amount':total_amount}
	dic.update(get_cart_len(request,"CUSTOMER"))
	return dic

def get_wishlist_items(request,user_type):
	if user_type == "CUSTOMER":
		wishlistobj = Wishlist.objects.filter(customer__user=request.user)
	else:
		wishlistobj = Wishlist.objects.filter(vendor__user=request.user)
	
	total_amount = 0
	tax_amount = 0
	subtotal_amount = 0	
	lt = []
	for x in wishlistobj:
		price = x.productvariants.saleprice()
		tax = round(((x.productvariants.product.tax * price) / 100),2)
		total = round((price * x.quantity),2)
		
		dic = {
		'id':x.id,
		'image':x.productvariants.productimage.url,
		'name':x.productvariants.productvariantname,
		'quantity':x.quantity,
		'price':price,
        'mrp':x.productvariants.mrp,
        'tax':tax,
		'total': total,
		'product_id':x.productvariants.id,}	
		if x.productvariants.quantity == 0:
			dic.update({'stock_out':True})
		else:
			dic.update({'stock_out':False})
		lt.append(dic)
	dic = {'items':lt, 'wishlist':wishlistobj}
	dic.update(get_wishlist_len(request,'CUSTOMER'))
	return dic


def fetch_pv(user):
	if UserPV.objects.filter(user=user).exists():
		usrpv = UserPV.objects.get(user=user)
		return {'left':usrpv.left_pv, 'right':usrpv.right_pv, 'level':usrpv.level_pv}
	else:
		UserPV.objects.create(user=user)
		usrpv = UserPV.objects.get(user=user)
		return {'left':usrpv.left_pv, 'right':usrpv.right_pv, 'level':usrpv.level_pv}
	
def fetch_pv_transactions(user):
	nodes = fetch_nodes(user)
	if nodes is not None:
		left_nodes = nodes['left']
		right_nodes = nodes['right']
		trans = []
		for x in left_nodes:
			for y in PVTransactions.objects.filter(user=x).order_by('-transaction_date'):
				trans.append(y)
		for x in right_nodes:
			for y in PVTransactions.objects.filter(user=x).order_by('-transaction_date'):
				trans.append(y)
		return trans
	else:
		print('nodes has none  value')

def fetch_user_tree(user):
	nodes = fetch_nodes(user)
	print(nodes,'NNNN')
	left_nodes = nodes['left']
	right_nodes = nodes['right']
	left = []
	right = []
	for x in left_nodes:
		node = MLM.objects.get(node=x)
		dic = {'node':x.usr.first_name+' '+x.usr.last_name, 'user':x.usr.user.id, 'parent':node.parent.usr.first_name+' '+node.parent.usr.last_name,'pv':fetch_pv(x)}
		left.append(dic)
	for x in right_nodes:
		node = MLM.objects.get(node=x)
		dic = {'node':x.usr.first_name+' '+x.usr.last_name, 'user':x.usr.user.id, 'parent':node.parent.usr.first_name+' '+node.parent.usr.last_name,'pv':fetch_pv(x)}
		right.append(dic)
	return {'left':left, 'right':right}

def get_user_indecater(user):
	pv=fetch_pv(user)
	total_pv = pv['left'] + pv['right'] + pv['level']
	subscribe = user.usr.subscribed
	if ((pv['level'] > 0.0) or subscribe) and (pv['left']+pv['right'] >= 50):
		return {'indicator': 'Stage 3'}
	elif (pv['level'] > 0.0) or subscribe:
		return {'indicator': 'Stage 2'}
	elif (pv['left']+pv['right'] >= 50):
		return {'indicator': 'Stage 1'}
	else:
		return {'indicator': 'Stage 0'}

def get_user_wallet(usertype,user):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
		traid=customer.id
		if not Wallet.objects.filter(customer=customer).exists():
			wallet=Wallet.objects.create(customer=customer,isactive=True)
		else:
			wallet = Wallet.objects.filter(customer=customer,isactive=True).first()
      
	elif usertype == "VENDOR":
		vendor=Vendor.objects.filter(user=user).first()
		traid=vendor.id
		if not Wallet.objects.filter(vendor=vendor).exists():
			wallet=Wallet.objects.create(vendor=vendor,isactive=True)
		else:
			wallet = Wallet.objects.filter(vendor=vendor,isactive=True).first()
	elif usertype == "ADMIN":
		admin=user
		traid=user.id
		if not Wallet.objects.filter(admin=admin).exists():
			wallet=Wallet.objects.create(admin=admin,isactive=True)
		else:
			wallet = Wallet.objects.filter(admin=admin,isactive=True).first()

	return {'wallet': wallet}


def check_user_subscription(user):
	if UserSubscription.objects.filter(user=user).exists():
		subs = UserSubscription.objects.get(user=user)
		days = subs.months * 30
		subscribed_on = subs.subscrbe_on
		future_date = subscribed_on + timedelta(days=days)
		if not future_date > subscribed_on:
			UserData.objects.filter(user=user).update(subscribed=False)
			UserSubscription.objects.filter(user=user).delete()
			return False
		else:
			return True



