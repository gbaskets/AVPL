from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from django.utils.html import format_html
	
admin.site.site_header="AVPL ADMIN"
admin.site.site_title="AVPL Admin Panel"
admin.site.index_title="Welcome to AVPL Admin Panel"

from django.contrib.auth.admin import UserAdmin

admin.site.register(UserOTP)

admin.site.register(WithdrawRequest)
admin.site.register(TaxLog)

class MyUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 
                           'groups', 'user_permissions')
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            perm_fields = ('is_active', 'is_staff')

        return [(None, {'fields': ('username', 'password')}),
                (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (('Permissions'), {'fields': perm_fields}),
                (('Important dates'), {'fields': ('last_login', 'date_joined')})]

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Address)
admin.site.register(PaymentTransaction)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(CommissionWallet)
admin.site.register(CommissionWalletTransaction)
admin.site.register(TDSLogWallet)
admin.site.register(TDSLogWalletTransaction)
admin.site.register(Notification)
admin.site.register(WalletBalanceTransfer)
admin.site.register(BusinessLimitWallet)

