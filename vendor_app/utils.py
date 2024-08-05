import random

from django.http import JsonResponse
from accountant_app.models import Account
from main_app.models import *
import barcode
from barcode import EAN13
from barcode.writer import ImageWriter
from django.core.files import File
from io import BytesIO

from sales_app.models import SalesOrder



def Trading_Account_Profit_and_Loss(storeobj):
    
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
        Account.objects.filter(store=storeobj,accountname="Profit & Loss").update(openingbalance=gross_profit,transctiontype='CREDIT')
    else:
        trading_data["Gross Loss"]["credit"] = -gross_profit
        Account.objects.filter(store=storeobj,accountname="Profit & Loss").update(openingbalance=-(gross_profit),transctiontype='DEBIT')

    return JsonResponse(trading_data)




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
