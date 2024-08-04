from django.contrib import admin
from django.urls import path
from vendor_app.views import *

urlpatterns = [
    path('', vendor_dashboard),
    path('order_status_update',order_status_update,name='order_status_update'),
  
    
    path('verification', vendor_doc),
    path('storeinfo', store_info),
    path('add-new-store', add_new_store),
    
    
    path('store',Store_list),
    path('store-selected',Store_Selected_List),
    
    path('profile', vendor_profile),
    path('edit-profile', edit_vendor_profile),
    path('get_businesscategory', get_businesscategory),
  
    path('product-list', vendor_product_list),
    path('add-product', add_product),
    path('edit-product/<int:id>', edit_product),
    
    
    path('product-variants-all-list/', vendor_product_variants_all_list),
    path('product-variants-list/<int:id>', vendor_product_variants_list),
    path('add-product-variants/<int:id>', add_product_variants),
    path('edit-product-variants/<int:id>', edit_product_variants),
    path('delete-product-variants/<int:pk>/<int:id>', delete_product_variants),
    
  

 
    path('orders', vendor_orders),
    path('purchases', vendor_purchases),
    path('orderdetail', vendor_order_detail),
    path('returndetail', vendor_return_details),
    

    path('changereturnstatus', vendor_change_return_status),
    

    

    path('deleteproductimage', vendor_delete_product_image),
    path('outofstock', vendor_product_out_of_stock),
    path('paymenttransactions', vendor_payment_transactions),
    path('wallet', vendor_wallet_dash),
    path('wallet-commission', vendor_wallet_commission_dash),
    path('withdraw', vendor_withdraw),
    path('help', vendor_help),
    #recharge
    path('businesslimit', vendor_Business_limit_dash),
    path('businesslimittransaction', vendor_recharge),
    path('capturerecharge', capture_recharge_payment),
    
    path('billing/requests/',vendor_billing_requests),
    path('billing/requests/confirm/', vendor_confirm_billing_requests),
    path('userSubscriptionRequest',userSubscriptionRequest),
    path('activateusersubscription',vendor_activate_subscription),
    path('balanacetransfer', vendorbalanacetransfer, name='balanacetransfer'),
    path('selfbalanacetransfer', vendorselfbalanacetransfer, name='selfbalanacetransfer'),
    path('otpvalidation', transfer_amount_vendor, name='otpvalidation'),
    path('creditedmoney', creditedmoney_user_wallet),
    
    path('add-chart-of-account', addchartofaccounts),
    path('edit-chart-of-account/<int:id>', editchartofaccounts),
    path('chart-of-account', chartofaccounts),
    path('account-ledger-transactions-history/<int:id>', accountledgertransactionshistory),
    

    
    path('manual-journal', manualjournal),
    path('add-manual-journal', add_manualjournal),
    path('view-manual-journal/<int:id>', view_manualjournal),
    
    
    path('purchase-vouchers', Purchase_Vouchers),
    path('purchase-vouchers/<int:id>', Purchase_Vouchers_Details),
    path('add-purchase-voucher', Add_Purchase_Vouchers),
    
    path('sales-vouchers', Sales_Vouchers),
    path('sales-vouchers/<int:id>', Sales_Vouchers_Details),
    path('add-sales-voucher', Add_Sales_Vouchers),
    
    
    path('fetch_productvaraints_related_data', fetch_productvaraints_related_data),
    
    path('fetch_productvaraints_sales_related_data', fetch_productvaraints_sales_related_data),
    
    
    
    path('Trial_Balance/',Trial_Balance),
    path('Trading_Account/',Trading_Account),
    path('Balance_Sheet/',Balance_Sheet),
    
    
    path('report/trial-balance', viewtrialBalance),
    path('report/trading-account', viewtradingaccount),
    path('report/balance-sheet', viewbalancesheet),
    
    
  

]