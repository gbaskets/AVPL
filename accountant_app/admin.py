from django.contrib import admin

# Register your models here.
from .models import *
# Register your models here.
admin.site.register(AccountTypeGroup)
admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(ManualJournalVoucher)
admin.site.register(AccountEntry)
admin.site.register(AccountTransaction)
