from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


# Register your models here.
from .models import *

class AccountTypeGroupAdmin(ImportExportModelAdmin,admin.ModelAdmin):
	...
admin.site.register(AccountTypeGroup,AccountTypeGroupAdmin)
class AccountTypeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
	...
admin.site.register(AccountType,AccountTypeAdmin)
class AccountTypeListAdmin(ImportExportModelAdmin,admin.ModelAdmin):
	...
admin.site.register(AccountTypeList,AccountTypeListAdmin)
admin.site.register(Account)
admin.site.register(ManualJournalVoucher)
admin.site.register(AccountEntry)
admin.site.register(AccountTransaction)

