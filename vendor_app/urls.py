from django.contrib import admin
from django.urls import path
from vendor_app.views import *

urlpatterns = [
    path('', vendor_dashboard),
    path('order_status_update',order_status_update,name='order_status_update'),
    path('order_status_updates',order_status_updates,name='order_status_updates'),
    
    path('verification', vendor_doc),
    path('storeinfo', store_info),
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
    
  
    path('product', vendor_product),
    path('update-product/<int:id>/', vendor_update_product_quantity,name='update-product'),
    path('productbasicedit', vendor_product_basic_edit),
    path('orders', vendor_orders),
    path('orderdetail', vendor_order_detail),
    path('returndetail', vendor_return_details),
    
    path('changeorderstatus', vendor_change_order_status),
    path('changereturnstatus', vendor_change_return_status),
    

    
    path('brand', vendor_brand),
    path('deleteproductimage', vendor_delete_product_image),
    path('deleteproductvariant', vendor_delete_product_variant),
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
    path('otpvalidation', transfer_amount_vendor, name='otpvalidation'),


]
