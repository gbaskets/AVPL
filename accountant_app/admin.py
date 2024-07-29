from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


# Register your models here.
from .models import *
# Register your models here.
admin.site.register(AccountTypeGroup)
admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(ManualJournalVoucher)
admin.site.register(AccountEntry)
admin.site.register(AccountTransaction)
admin.site.register(AccountTypeList)

