from django.contrib import admin
from django.urls import path
from admin_app.views import *
from admin_app.utils import *

urlpatterns = [
    path('', admin_login),
    path('dashboard', admin_dashboard),
    path('show', admin_show),
    path('bussiness-main-categories', admin_bussiness_main_categories),
    path('add-bussiness-main-categories', admin_add_bussiness_main_categories),
    path('edit-bussiness-main-categories/<int:id>', admin_edit_bussiness_main_categories, name="edit-bussiness-main-categories"),
    path('delete-bussiness-main-categories/<int:id>', admin_delete_bussiness_main_categories, name="delete-bussiness-main-categories"),
    path('bussiness-categories', admin_bussiness_categories),
    path('add-bussiness-categories', admin_add_bussiness_categories),
    path('edit-bussiness-categories/<int:id>', admin_edit_bussiness_categories, name="edit-bussiness-categories"),
    path('delete-bussiness-categories/<int:id>', admin_delete_bussiness_categories, name="delete-bussiness-categories"),

    path('product-brands', admin_product_brands),
    path('add-product-brands', admin_add_product_brands),
    path('edit-product-brands/<int:id>', admin_edit_product_brands, name="edit-product-brands"),
    path('delete-product-brands/<int:id>', admin_delete_product_brands, name="delete-product-brands"),
    
    path('product-units', admin_product_units),
    path('add-product-units', admin_add_product_units),
    path('edit-product-units/<int:id>', admin_edit_product_units, name="edit-product-units"),
    path('delete-product-units/<int:id>', admin_delete_product_units, name="delete-product-units"),
    
    path('product-firstvariant', admin_product_firstvariant),
    path('add-product-firstvariant', admin_add_product_firstvariant),
    path('edit-product-firstvariant/<int:id>', admin_edit_product_firstvariant, name="edit-product-firstvariant"),
    path('delete-product-firstvariant/<int:id>', admin_delete_product_firstvariant, name="delete-product-firstvariant"),
    
    path('product-firstvariantvalue', admin_product_firstvariantvalue),
    path('add-product-firstvariantvalue', admin_add_product_firstvariantvalue),
    path('edit-product-firstvariantvalue/<int:id>', admin_edit_product_firstvariantvalue, name="edit-product-firstvariantvalue"),
    path('delete-product-firstvariantvalue/<int:id>', admin_delete_product_firstvariantvalue, name="delete-product-firstvariantvalue"),
    
    
    path('product-secondvariant', admin_product_secondvariant),
    path('add-product-secondvariant', admin_add_product_secondvariant),
    path('edit-product-secondvariant/<int:id>', admin_edit_product_secondvariant, name="edit-product-secondvariant"),
    path('delete-product-secondvariant/<int:id>', admin_delete_product_secondvariant, name="delete-product-secondvariant"),
    
    path('product-secondvariantvalue', admin_product_secondvariantvalue),
    path('add-product-secondvariantvalue', admin_add_product_secondvariantvalue),
    path('edit-product-secondvariantvalue/<int:id>', admin_edit_product_secondvariantvalue, name="edit-product-secondvariantvalue"),
    path('delete-product-secondvariantvalue/<int:id>', admin_delete_product_secondvariantvalue, name="delete-product-secondvariantvalue"),
    
    path('product-thirdvariant', admin_product_thirdvariant),
    path('add-product-thirdvariant', admin_add_product_thirdvariant),
    path('edit-product-thirdvariant/<int:id>', admin_edit_product_thirdvariant, name="edit-product-thirdvariant"),
    path('delete-product-thirdvariant/<int:id>', admin_delete_product_thirdvariant, name="delete-product-thirdvariant"),
    
    path('product-thirdvariantvalue', admin_product_thirdvariantvalue),
    path('add-product-thirdvariantvalue', admin_add_product_thirdvariantvalue),
    path('edit-product-thirdvariantvalue/<int:id>', admin_edit_product_thirdvariantvalue, name="edit-product-thirdvariantvalue"),
    path('delete-product-thirdvariantvalue/<int:id>', admin_delete_product_thirdvariantvalue, name="delete-product-thirdvariantvalue"),
    
    path('product-categories', admin_product_categories),
    path('add-product-categories', admin_add_product_categories),
    path('edit-product-categories/<int:id>', admin_edit_product_categories, name="edit-product-categories"),
    path('delete-product-categories/<int:id>', admin_delete_product_categories, name="delete-product-categories"),
    
    path('product-subcategories', admin_product_subcategories),
    path('add-product-subcategories', admin_add_product_subcategories),
    path('edit-product-subcategories/<int:id>', admin_edit_product_subcategories, name="edit-product-subcategories"),
    path('delete-product-subcategories/<int:id>', admin_delete_product_subcategories, name="delete-product-subcategories"),
    
    path('product-sub-subcategories', admin_product_subsubcategories),
    path('add-product-sub-subcategories', admin_add_product_subsubcategories),
    path('edit-product-sub-subcategories/<int:id>', admin_edit_product_subsubcategories, name="edit-product-sub-subcategories"),
    path('delete-product-sub-subcategories/<int:id>', admin_delete_product_subsubcategories, name="delete-product-sub-subcategories"),
    
    path('product', admin_product),
    path('productapproval', admin_product_approval),
    path('all-products', admin_product_list),
    
    
    path('vendorprofile', admin_vendor_profile),
    path('editvendorprofile', admin_edit_vendor_profile),

    path('vendor-commission-wallet', admin_vendor_commission_wallet),
    path('vendor-commission-wallet/<int:id>',admin_vendor_commission_wallet_details, name='vendor-commission-wallet'),
    path('activate_is_commission_wallet', admin_activate_is_commission_wallet_vendor),
    path('deactivate_is_commission_wallet', admin_deactivate_is_commission_wallet_vendor),




    path('admin_pv', admin_pv_wallet),
   
    path('vendor-verification', admin_vendor_verification),
    path('activatevendor', admin_activate_vendor),
    path('activateisavplvendor', admin_activate_approved_avpl_vendor),
    path('point/', admin_point_value),
    path('createlink', admin_create_link),
    path('generatelink-left', admin_generate_link_left),
    path('generatelink-right', admin_generate_link_right),
    path('undertrees', admin_under_trees),
    path('binary/genealogyTree', genealogyTree_binary),
    path('level/genealogyTree', genealogyTree_level),
    path('level/underlevel', admin_under_trees_level),
    path('deliverycharges', admin_delivery_charges),
    path('vendor-list', admin_vendor_list),
    path('activate_isavplvendor', admin_is_activate_approved_avpl_vendor),
    path('deactivate_isavplvendor', admin_is_deactivate_approved_avpl_vendor),

    
    path('paymentinfo', admin_payment_info),
    path('orders', admin_orders),
    path('setpvpair', admin_pvpairvalue),
    path('leadershipbonus', admin_leadership_bonus_set),
    path('housefund', admin_house_fund_set),
    path('carfund', admin_car_fund_set),
    path('directorshipfund', admin_directorship_fund_set),
    path('travelfund', admin_travel_fund_set),
    path('sendmoney', admin_send_money),
    path('sendmoneyotpvalidations', sendmoneytransfer_admin, name='sendmoneyotpvalidations'),

    path('withdraw', admin_withdraw),
    path('changewithdrawstatus', admin_change_withdraw_status),
    path('query', admin_query),
    path('queryresult', admin_query_result),
    path('changequerystatus', admin_change_query_status),
    path('setpvconversion', admin_set_pv_conversion),
    
   
    path('productbasicedit', admin_product_basic_edit),
    path('deleteproductimage', admin_delete_product_image),
    path('deleteproductvariant', admin_delete_product_variant),
    path('outofstock', admin_product_out_of_stock),
    path('activateproduct', admin_activate_product),
    path('sendqueryreply', admin_query_send_reply),
    path('wallet_details', wallet_details),
    path('wallet_details/wallet-recharge', admin_wallet_recharge),
    
    path('tax', admin_taxation),
   
    path('users', admin_users),
    path('users/delete', admin_users_delete),
    # Per Product Vendor Commission
    
    path('vendorcommission',vendor_commission),
    #path for User commission for refered vendor
    path('uservendorcommission', user_vendor_commission),
    path('settings/', admin_level_settings),
    path('fetchgroups/', admin_fetch_groups),
    path('edit/group/', admin_edit_group),
    path('level/settings/', admin_level_settings_level_plan),
    path('level/fetchgroups/', admin_fetch_groups_level),
    path('level/edit/group/', admin_edit_group_level),
    path('minmumcartvalue/', admin_min_cart_value),
    path('billing/config/', admin_billing_config),
    path('product/reject/', admin_reject_product),
    path('product/update/', admin_update_product),
    path('gst_log/', admin_gst_log),
    path('total_tds', admin_total_tds),
    path('tds_log/', admin_tds_withdraw),
    path('tds_log_details/<int:id>',admin_tds_log_details, name='tds_log_details'),
    path('contact', contact),
    path('terms', terms),
    path('privacy', privacy),
    path('about-us', admin_about_us),
    path('gallery', admin_gallery),
    path('blog', admin_blog),
    path('banner', admin_banner),
    path('direct-referal', admin_direct_referal),

    path('subscription-pack',admin_subscription_pack),
    path('userSubscriptionRequest',userSubscriptionRequest_admin),

    path('balanacetransfers', adminbalanacetransfer, name='balanacetransfers'),
    path('otpvalidations', transfer_amount_admin, name='otpvalidations'),

    path('staff_list', staff_list,),
    path('activate_is_active', admin_activate_isactive_staff),
    path('deactivate_is_active', admin_deactivate_isactive_staff),

    path('staffprofile', admin_staff_profile),
    path('staff_delete', admin_staff_delete),

   


    
]