import random
from main_app.models import *
import barcode
from barcode import EAN13
from barcode.writer import ImageWriter
from django.core.files import File
from io import BytesIO


def get_order_details(order_id):
	order = OrderItems.objects.get(id=order_id)
	print(order.total)
	image = ProductImages.objects.filter(product=order.product)[0]
	variants = OrderItemVariant.objects.filter(orderitem=order)
	dic = {'order':order, 'image':image.image.url, 'variants':variants}
	return dic



def generate_bracode(unique_barcode):
    EAN = barcode.get_barcode_class('ean13')
    if unique_barcode == "":
        barcode_number =  random.randint(100000000000, 9999999999999)
    else:
        barcode_number=unique_barcode
    ean = EAN(f'{barcode_number}', writer = ImageWriter())
    barcode_unique_no = ean
    buffer = BytesIO()
    ean.write(buffer)
    pic = f'ean.png',File(buffer)
    
    return [File(buffer),barcode_unique_no]



def generate_code(id,arry=[]):
    
    code=""
    for a in arry:
        name=""
        v = True
        for i in range(len(a)):
            if (a[i] == ' '):
                v = True
            elif (a[i] != ' ' and v == True):
                name += (a[i])
                v = False
        code+=name
        
    return code + str(id)
