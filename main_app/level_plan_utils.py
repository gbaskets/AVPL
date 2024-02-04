from django.contrib.auth.models import User
from django.contrib import messages
from main_app.models import *
from user_app.models import *

def add_to_level_plan(request):
	 
	print(request.session['parent'],'1111PPPPPPPPPPPppp')
	parent = Level_Plan_Sponsors.objects.filter(sponsors__id=request.session['parent']).first()
	print(parent,'PPPPPPPPPParent')
	if parent:
		child_obj = User.objects.get(id=request.session['child'])
		if not Level_Plan_Referrals.objects.filter(referrals=child_obj).exists():
			parent_obj 					  = Level_Plan_Referrals()
			parent_obj.level_plan_sponsor = parent 
			parent_obj.referrals          = child_obj
			parent_obj.save() 
			messages.success(request, 'You have been add under admin')
		else:
		    messages.warning(request, 'Already created !')
	else:
		child_obj = User.objects.get(id=request.session['child'])
		print(child_obj,'CCCCCCCCCCCCCChild')
		if not Level_Plan_Referrals.objects.filter(referrals=child_obj).exists():
			print(request.session['parent'],'2222PPPPPPPPPPPppp')
			parent_obj  = Level_Plan_Referrals.objects.filter(referrals__id=request.session['parent']).first()
			print(parent_obj,'Parenobjjjjj')
			referral_obj = Level_Plan_Referrals()
			referral_obj.level_plan_referral = parent_obj
			referral_obj.referrals = child_obj
			referral_obj.save()
			messages.success(request, 'You have been add under '+parent_obj.referrals.first_name)
		else:
			messages.warning(request, 'Already created !')

def calculate_point_value_on_order(cart):
	cartitems = CartItems.objects.filter(cart=cart)
	total_pv = 0.0
	for x in cartitems:
		pv_percent = PointValue.objects.get(category=x.product.category)
		pv = (x.total_cost/100)*pv_percent.percentage
		total_pv = total_pv + pv
	return total_pv
