import razorpay
from main_app.models import *
from vendor_app.models import *

# client = razorpay.Client(auth=("rzp_live_x7PnIDVsQs52F2", "suxN8QoVA16C6QeRV0hjexWU"))
client = razorpay.Client(auth=("rzp_test_OcvfBakbfEdBxL", "tLlVOve6xEK1DwoqYgjVBI8i"))

# client = razorpay.Client(auth=("rzp_test_QOX9qreyce5Ewm", "FJx9ZVKVzVNlQBCemV2qQvuf"))


def create_online_order(cartobj, address,usertype, user,paymentgatway):
	if usertype == "CUSTOMER":
		customer=Customer.objects.filter(user=user).first()
	elif usertype == "VENDOR":
		vendor=Vendor.objects.filter(user=user).first()
	elif usertype == "ADMIN":
		admin=User.objects.filter(user=user).first()
  
	total_amount=cartobj['total_amount']
	tax_amount=cartobj['tax_amount']
	subtotal_amount=cartobj['subtotal_amount']
		
	order_amount = int(total_amount)
	order_currency = 'INR'
	order_receipt = cartobj["items"][0]["id"]
	print('jhgbjhgbjh', order_amount,order_currency, order_receipt)
	if address.firstname and  address.lastname :
		fullname= f'{address.firstname} {address.lastname}'
	else:
		fullname= address.firstname 
	address_val = fullname +', '+address.streetaddress+', '+address.nearbyaddress+' '+address.city+' '+address.state+' '+ str(address.mobile)
	notes = {'Shipping address': address_val}   # OPTIONAL
	dic = {
	'amount' : order_amount * 100,
	'currency' : order_currency,
	'receipt' : str(order_receipt),
	'notes' : notes,
	'payment_capture': 0
	}
	data = client.order.create(data=dic)

	order_id = data['id']
	razorpay_order_id=data['id']
	print(order_id,'razorpay_order_idrazorpay_order_id')
	paymenttransactionobj=PaymentTransaction()
	paymenttransactionobj.customer = customer
	paymenttransactionobj.paymentgatway=paymentgatway
	paymenttransactionobj.transactionid =razorpay_order_id
	paymenttransactionobj.transactionrealted= 'PRODUCT-ORDER'
	paymenttransactionobj.transactiondetails =f'Order product Rs.{order_amount}/- by {customer.user.username}'
	paymenttransactionobj.amount = order_amount
	paymenttransactionobj.address = address
	paymenttransactionobj.save()
	return data

def create_razorpay_order(receipt_id, user, amount):
	order_amount = amount
	order_currency = 'INR'
	order_receipt = str(receipt_id)
	notes = {}   # OPTIONAL
	dic = {
	'amount' : order_amount,
	'currency' : order_currency,
	'receipt' : order_receipt,
	'notes' : notes,
	'payment_capture': 0
	}
	print('loading...')
	data = client.order.create(data=dic)
	Recharge_Receipt.objects.filter(id=receipt_id).update(razorpay_order_id=data['id'])
	return data


# def create_razorpay_order2(receipt_id, user, amount):
# 	order_amount = amount
# 	order_currency = 'INR'
# 	order_receipt = str(receipt_id)
# 	notes = {}   # OPTIONAL
# 	dic = {
# 	'amount' : order_amount,
# 	'currency' : order_currency,
# 	'receipt' : order_receipt,
# 	'notes' : notes,
# 	'payment_capture': 0
# 	}
# 	print('loading...')
# 	data = client.order.create(data=dic)
# 	Memberip_Receipt.objects.filter(id=receipt_id).update(razorpay_order_id=data['id'])
# 	return data
# def fetch_all_orders():
# 	print('hello')
