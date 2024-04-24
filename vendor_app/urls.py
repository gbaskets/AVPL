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
  
    path('addproduct', add_product),
    path('addproductimages', add_product_images),
    path('addproductvariant', add_product_variant),
    path('fetchsubcategory', fetch_sub_category),
    path('fetchsubsubcategory', fetch_sub_sub_category),
    path('productlist', vendor_product_list),
  
    path('product', vendor_product),
    path('update-product/<int:id>/', vendor_update_product_quantity,name='update-product'),
    path('productbasicedit', vendor_product_basic_edit),
    path('fetchvariantvalue', fetch_variant_value),
    path('orders', vendor_orders),
    path('orderdetail', vendor_order_detail),
    path('returndetail', vendor_return_details),
    
    path('changeorderstatus', vendor_change_order_status),
    path('changereturnstatus', vendor_change_return_status),
    
    path('completeorders', vendor_complete_orders),
    # path('returnorders', vendor_return_orders),
    
    path('brand', vendor_brand),
    path('fetchbrands', fetch_brands),
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
