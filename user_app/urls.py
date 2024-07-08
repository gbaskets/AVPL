from django.urls import path
from user_app.views import *

urlpatterns = [
    path('', user_dashboard),
    path('createuser', create_user),
    path('createlink', user_create_link),
    path('generatelink-left', user_generate_link_left),
    path('generatelink-right', user_generate_link_right),
    path('generatelink2-left', user_generate_link_2_left),
    path('generatelink2-right', user_generate_link_2_right),
    path('addtocart', user_add_to_cart),
    path('addtowishlist', add_to_wishlist),
    
    path('cart', user_cart),
    path('wishlist', user_wishlist),
    path('updatecartitem', update_cart_item),
    path('removecartitem', remove_cart_item),
    path('removewishlistitem', remove_wishlist_item),
    
    path('myaddress', my_address),
    path('myorder', my_order),
    path('myorder-details', my_order_details),
    path('savelocation', save_location),
    path('enableselfpickup', enable_self_pickup),
    path('add_new_address', add_new_address),
    path('wallet', user_wallet),
    path('tree', user_tree),
    path('binary/genealogyTree', genealogyTree_binary),
    path('level/genealogyTree', genealogyTree_level),
    path('setdefaultaddress', user_set_default_address),
    path('saverating', user_save_product_rating),
    path('pvwallet', user_pv_wallet),
    path('withdraw', user_withdraw),
    path('help', user_help),
    path('productquery', user_product_query),
    path('cancelorder', user_cancel_order),
    path('cancelconfirm', cancel_confirm),
    path('generateinvoice', user_generate_invoice),
    #showing user Vendor Relation
    path('createvendorlink', create_vendor_link),
    path('generatevendorlink', user_vendor_generate_link),

    path('subscription/',subscription_amount),
    path('capturerecharge', capture_recharge_payment),
    path('vendor_list/',vendor_list),
    path('subscriptionRequest/',subscriptionRequest),
    path('billing/request/', user_billing_request),
	path('direct-referal/',direct_referal),

    path('tds_log/', user_tds_withdraw),
    path('referal_transaction/', referal_transaction),

    path('vendor-wallet-transfer/',wallet_transfer_vendor,name='vendor-wallet-transfer'),
    path('otp-verification/',transfer_amount,name='otp-verification'),
    path('profile', user_profile),
    path('edit-profile', edit_customer_profile),
    path('creditedmoney', creditedmoney_user_wallet),
 



]