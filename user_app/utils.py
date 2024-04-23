from datetime import timedelta
from user_app.models import *
from main_app.utils import *
from main_app.mlm_utils import *
from vendor_app.models import *
from django.utils import timezone

def get_cart_len(request):
	if request.user.is_authenticated:
		if Cart.objects.filter(customer__user=request.user).exists():
			cart = Cart.objects.get(customer__user=request.user)
			cart_len=len(cart)
		else:
			cart_len = 0
		
		dic = {'cart_len':cart_len}
		return dic
	else:
		dic = {'cart_len':0}
		return dic

def get_wishlist_len(request):
	if request.user.is_authenticated:
		if Wishlist.objects.filter(customer__user=request.user).exists():
			cart = Wishlist.objects.get(customer__user=request.user)
			wish_len=len(cart)
		else:
			wish_len = 0
		
		dic = {'wish_len':wish_len}
		return dic
	else:
		dic = {'wish_len':0}
		return dic

def get_cart_items(request):
	cart = Cart.objects.get(user=request.user)
	print(cart)
	lt = []
	for x in CartItems.objects.filter(cart=cart):
		image = ProductImages.objects.filter(product=x.product)[0]
		dic = {
		'id':x.id,
		'image':image.image.url,
		'name':x.product.name,
		'quantity':x.quantity,
		'price':x.per_item_cost,
		'total':x.total_cost,
		'stock':x.product.stock,
		'product_id':x.product.id,
		'tax':x.product.category.tax
		}	
		variant = []
		print("xxxxxxxx", x)
		for y in CartItemVariant.objects.filter(cartitem=x):
			print("y111	", y)
			variant.append(y.product_variant)
		dic.update({'variant':variant})
		if x.product.stock == 0:
			dic.update({'stock_out':True})
		else:
			dic.update({'stock_out':False})
		lt.append(dic)
	dic = {'items':lt, 'cart':cart}
	dic.update(get_cart_len(request))
	return dic

def get_wishlist_items(request):
	cart = Wishlist.objects.get(user=request.user)
	lt = []
	for x in WishlistItems.objects.filter(wishlist=cart):
		image = ProductImages.objects.filter(product=x.product)[0]
		dic = {
		'id':x.id,
		'image':image.image.url,
		'name':x.product.name,
		'mrp':x.product.mrp,
		'price':x.product.price,
		'offer':x.product.offer,
		'weight':x.product.weight,
		'store':x.product.store.name,
		'brand':x.product.brand.name,
		'description':x.product.description,
		'quantity':x.quantity,
		'price':x.per_item_cost,
		'total':x.total_cost,
		'stock':x.product.stock,
		'product_id':x.product.id
		}	
		variant = []
		print("xxxxxxxx", x)
		for y in WishlistItemVariant.objects.filter(wishlistitem=x):
			print("y111	", y)
			variant.append(y.product_variant)
		dic.update({'variant':variant})
		if x.product.stock == 0:
			dic.update({'stock_out':True})
		else:
			dic.update({'stock_out':False})
		lt.append(dic)
	dic = {'items':lt, 'cart':cart}
	dic.update(get_wishlist_len(request))
	return dic

def calculate_cart_tax(request):
	cart = Cart.objects.get(user=request.user)
	tax = 0.0
	for item in CartItems.objects.filter(cart=cart):
		cate_tax = item.product.category.tax
		print("cate_tax")
		print(cate_tax)
		#item_tax = (item.total_cost/100)*cate_tax
		print("item_tax")
		print("tax")
	delivery_charge = 0.0
	check_user_subscription(request.user)
	if request.user.usr.subscribed:
		total = cart.subtotal + ((cart.subtotal*cate_tax)/100)
		print(total,'3333333')
		# total = cart.subtotal
	else:
		#if cart.subtotal <= 999.0:	
		for x in DeliveryCharge.objects.all():
			delivery_charge = x.amount
		#total = cart.subtotal + tax + delivery_charge
		if cart.total < 500:
			if cart.self_pickup == False:
				total = cart.subtotal  + delivery_charge + ((cart.subtotal*cate_tax)/100)
				print(total,'3333333333')
			elif cart.self_pickup == True:
				total = cart.subtotal + ((cart.subtotal*cate_tax)/100)
				print(total,'2222222')
		else:
			total = cart.subtotal + ((cart.subtotal*cate_tax)/100)
			print(total,'111111')
	Cart.objects.filter(user=request.user).update(tax=tax, total=total, delivery_charges=delivery_charge)
	Cart.objects.filter(user=request.user).update(total=total, delivery_charges=delivery_charge)

def get_my_orders(user, store=None):
	items = []
	for order in Orders.objects.filter(user=user).order_by('-order_date'):
		if store:
			for item in OrderItems.objects.filter(order=order, store=store):
				dic = {'item':item, 'rating_flag':False}
				variants = []
				for x in OrderItemVariant.objects.filter(orderitem=item):
					variants.append(x)
				dic.update({'variants':variants})
				for x in ProductImages.objects.filter(product=item.product):
					dic.update({'image':x.image.url})
					break
				if ProductRating.objects.filter(product=item.product, user=user).exists():
					dic.update({'rating_flag':True, 'rating':ProductRating.objects.get(product=item.product, user=user).rating})
				else:
					dic.update({'rating_flag':False})
				dic.update({'date':order.order_date})
				items.append(dic)
		else:
			for item in OrderItems.objects.filter(order=order):
				dic = {'item':item, 'rating_flag':False}
				variants = []
				for x in OrderItemVariant.objects.filter(orderitem=item):
					variants.append(x)
				dic.update({'variants':variants})
				for x in ProductImages.objects.filter(product=item.product):
					dic.update({'image':x.image.url})
					break
				if ProductRating.objects.filter(product=item.product, user=user).exists():
					dic.update({'rating_flag':True, 'rating':ProductRating.objects.get(product=item.product, user=user).rating})
				else:
					dic.update({'rating_flag':False})
				dic.update({'date':order.order_date})
				items.append(dic)
	return items

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

def get_user_wallet(user):
    
	if Wallet.objects.filter(user=user).exists:
		# Wallet.objects.create(user=user)
		wallet= Wallet.objects.filter(user=user).first()
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




def make_creditedmoney_transaction(user, amount, trans_type):
	if not CreditedMoney.objects.filter(user=user).exists():
		CreditedMoney.objects.create(user=user)
	creditedmoney = CreditedMoney.objects.get(user=user)
	print(creditedmoney)
	if trans_type == 'CREDIT':
		print('1')
		creditedmoney_transactions = CreditedMoneyTransaction.objects.create(
			creditedmoney = creditedmoney,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			previous_amount = round(creditedmoney.current_balance, 2),
			remaining_amount = round(creditedmoney.current_balance,2) + round(amount,2)
		)
		CreditedMoney.objects.filter(user=user).update(current_balance = round(creditedmoney.current_balance, 2) + round(amount, 2))


	elif trans_type == 'DEBIT':
		print(2)
		creditedmoney_transactions = CreditedMoneyTransaction.objects.create(
			creditedmoney = creditedmoney,
			transaction_date = timezone.now(),
			transaction_type = trans_type,
			transaction_amount = amount,
			previous_amount = creditedmoney.current_balance,
			remaining_amount = creditedmoney.current_balance - amount
		)
		print(creditedmoney)
		CreditedMoney.objects.filter(user=user).update(current_balance = creditedmoney.current_balance - amount)

	