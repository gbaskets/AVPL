from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from vendor_app.models import *
from main_app.models import *
from admin_app.models import *
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from  user_app.models import *

class ReferalCommissionSettings(models.Model):
	customer=models.FloatField(default=0.00)
	vendor=models.FloatField(default=0.00)
	admin=models.FloatField(default=0.00)
	directreferal=models.FloatField(default=0.00)
	isactive = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


class SubscriptionPlan(models.Model):
	name=models.CharField(max_length=255)
	description=RichTextField()
	duration=models.CharField(max_length=255)
	charge=models.FloatField(default=0.00)
	pvpercentage = models.FloatField(default=0.00)
	vendorpercentage = models.FloatField(default=0.00)
	isactive = models.BooleanField(default=False)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

# <----------- Level Settings for ---Binary Plan ---------------->

class LevelSettings(models.Model):
	levels = models.PositiveIntegerField()
	groups = models.PositiveIntegerField()
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	
class LevelGroup(models.Model):
	level = models.ForeignKey(LevelSettings, on_delete=models.CASCADE)
	percentperlevel = models.FloatField(default=1)
	nooflevels = models.PositiveIntegerField(default=1)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

# <----------- Level Settings for ---Level Plan ---------------->

class LevelSettingsLevelPlan(models.Model):
	levels = models.PositiveIntegerField()
	groups = models.PositiveIntegerField()
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

class LevelGroupLevelPlan(models.Model):
	level = models.ForeignKey(LevelSettingsLevelPlan, on_delete=models.CASCADE)
	percentperlevel = models.FloatField(default=1)
	nooflevels = models.PositiveIntegerField(default=1)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

class BillingConfiguration(models.Model):
	admincommission = models.FloatField(default=1)
	pvpercent = models.FloatField(default=1)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

class CurrentPV(models.Model):
	pv = models.FloatField(default=0.0)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


# class YearlyPV(models.Model):
# 	pv = models.FloatField(default=0.00)
# 	createdat = models.DateTimeField(auto_now_add=True)
# 	updatedon = models.DateTimeField(auto_now=True)
# 	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


# class MonthlyPV(models.Model):
# 	pv = models.FloatField(default=0.0)
# 	createdat = models.DateTimeField(auto_now_add= True)
# 	updatedon = models.DateTimeField(auto_now=True)




class BonusMLM (models.Model):
	typeofbonus=models.CharField(max_length=255)
	percentage = models.FloatField(default=0.00)
	target = models.PositiveIntegerField(default=100000)
	createdat = models.DateTimeField(auto_now_add=True)
	updatedon = models.DateTimeField(auto_now=True)
	updatedby= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return str(self.typeofbonus) + ' ' + str(self.percentage) 
	
# Create your models here.
class UserLinkType(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
	link=models.CharField(max_length=255,null=True,blank=True)
	links=models.CharField(max_length=255,null=True,blank=True)
	linktype= models.CharField(max_length=255,null=True,blank=True)


################# MLM Models ##############################################

############## Below model denotes the users under admin ##################
class MLMAdmin(models.Model):
	child = models.ForeignKey(User,on_delete=models.CASCADE, related_name='child')
	def __str__(self):
		return str(self.child)

################## User MLM Model #########################################
class MLM(models.Model):
	parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent')                                                         
	node = models.ForeignKey(User, on_delete=models.CASCADE, related_name='node')
	left = models.ForeignKey(User, on_delete=models.CASCADE, related_name='left', null=True, blank=True)
	right = models.ForeignKey(User, on_delete=models.CASCADE, related_name='right', null=True, blank=True)
	
	def __str__(self):
		return self.node.username

################## User (Level Plan Model -Combo Purchase) #########################################
class LevelPlanSponsors(models.Model):
	sponsors = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
	def __str__(self):
		return self.sponsors.username
	
class LevelPlanReferrals(models.Model):
	levelplansponsor=models.ForeignKey(LevelPlanSponsors, on_delete=models.CASCADE,null=True,blank=True)
	# referred for
	referrals = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
	# referred by
	levelplanreferral=models.ForeignKey('LevelPlanReferrals', on_delete=models.CASCADE,null=True,blank=True)

	def __str__(self):
		
		return self.referrals.username + ' ' + 'Id:' + str(self.referrals.id )


# class PVTransactions(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	previouspv = models.FloatField(default=0.0)
# 	pv = models.FloatField()
# 	totalpv = models.FloatField()
# 	plan = models.CharField(max_length=255,null=True,blank=True )

# 	def __str__(self):
# 		return 'Transaction ID '+str(self.id)

# #PV Under User
# class UserPV(models.Model):
# 	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userpv')
# 	rightpv = models.FloatField(default=0.0)
# 	leftpv = models.FloatField(default=0.0)
# 	levelpv = models.FloatField(default=0.0)
	
# 	def __str__(self):
# 		return str(self.user) +' Right PV '+str(self.rightpv)+' Left PV '+str(self.leftpv)
