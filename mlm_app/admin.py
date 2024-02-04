from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(ReferalCommissionSettings)
admin.site.register(SubscriptionPlan)
admin.site.register(LevelSettings)
admin.site.register(LevelGroup)
admin.site.register(LevelSettingsLevelPlan)
admin.site.register(LevelGroupLevelPlan)
admin.site.register(BonusMLM)
admin.site.register(UserLinkType)


admin.site.register(MLMAdmin)
admin.site.register(MLM)

admin.site.register(LevelPlanSponsors)
admin.site.register(LevelPlanReferrals)
