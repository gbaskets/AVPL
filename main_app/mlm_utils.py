from django.contrib.auth.models import User
from django.contrib import messages
from main_app.models import *
from user_app.models import *

def fetch_empty_nodesmlmleft(node):
	try:
		left = fetch_one_side_empty_nodesleft(node, [])
		return {'left':left}
	except MLM.DoesNotExist:
	    user = None

def fetch_one_side_empty_nodesleft(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None :
			members.append(node)
		return members
	else:
		return members

def fetch_empty_nodesmlmright(node):
	try:
		right = fetch_one_side_empty_nodesright(node, [])
		return {'right':right}
	except MLM.DoesNotExist:
	    user = None

def fetch_one_side_empty_nodesright(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.right == None :
			members.append(node)
		return members
	else:
		return members
	
		

def fetch_user_treess(user):
	nodes = fetch_nodes(user)
	left_nodes = nodes['left']
	right_nodes = nodes['right']
	left = []
	right = []
	for x in left_nodes:
		node = MLM.objects.get(node=x)
		dic = {'node':x, 'user':x.usr.user.id, 'parent':node.parent.usr.first_name+' '+node.parent.usr.last_name,}
		left.append(dic)
	for x in right_nodes:
		node = MLM.objects.get(node=x)
		dic = {'node':x , 'user':x.usr.user.id, 'parent':node.parent.usr.first_name+' '+node.parent.usr.last_name,}
		right.append(dic)
	return {'left':left, 'right':right}



def fetch_empty_nodes(node):
	try:
		mlm = MLM.objects.get(node=node)
		left = fetch_one_side_empty_nodes(mlm.left, [])
		right = fetch_one_side_empty_nodes(mlm.right, [])
		return {'left':left, 'right':right}
	except MLM.DoesNotExist:
	    user = None

def fetch_one_side_empty_nodes(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None and mlm.right != None:
			members.append(node)
			fetch_one_side_empty_nodes(mlm.right, members)
		elif mlm.right == None and mlm.left != None:
			members.append(node)
			fetch_one_side_empty_nodes(mlm.left, members)
		elif mlm.left != None and mlm.right != None:
			fetch_one_side_empty_nodes(mlm.left, members)
			fetch_one_side_empty_nodes(mlm.right, members)
		elif mlm.left == None and mlm.right == None:
			members.append(mlm.node)
		return members
	else:
		return members






def add_to_mlm(request):
	parent = User.objects.get(id=request.session['parent'])

	parent_type = request.session['parent_type']
	child = User.objects.get(id=request.session['child'])
	u= request.session ['u']
	print(u,'links-----------')
	link_type=UserLinkType.objects.filter(links=request.session ['u']).first()
	print(link_type.link_type,'LLLLLLLLLLLLL')

	treesss=fetch_empty_nodes(parent)
	print(treesss,'TTTT')

    
	if link_type.link_type == 'left':
		
		if parent_type == 'Admin':
			if not MLMAdmin.objects.filter(child=child).exists():
				MLMAdmin.objects.create(child=child)
			if not MLM.objects.filter(node=child).exists():
				MLM.objects.create(parent=parent, node=child)
				messages.success(request, 'You have been add under Admin')

				
		if parent_type == 'User':
			
			
			if MLM.objects.get(node=parent).left == None:
				MLM.objects.filter(node=parent).update(left=child)
			else:
				treesss=fetch_empty_nodes(parent)
				if treesss is not None:
					# count = 0
					for userl in treesss['left']:
						# if count < 1:
						left_empty=fetch_empty_nodesmlmleft(userl)
						for userleft in left_empty['left']:
							print(userleft,'LeftlllllllLLLL')
							if not MLM.objects.filter(node=userleft).exists():
								MLM.objects.filter(node=userleft).update(left=child)
							else:
		   						messages.warning(request, 'Already created !')
							# count += 1   
				
			if not MLM.objects.filter(node=child).exists():
				MLM.objects.create(parent=parent, node=child)
				messages.success(request, 'You have been add under '+parent.usr.first_name)
				print('LeftTTTTTTTTTTTTTTTTTT')
			else:
			    print('No node empty in left')
				
	if link_type.link_type == 'right':

		if parent_type == 'Admin':
			if not MLMAdmin.objects.filter(child=child).exists():
				MLMAdmin.objects.create(child=child)
			if not MLM.objects.filter(node=child).exists():
				MLM.objects.create(parent=parent, node=child)
				messages.success(request, 'You have been add under Admin')



		if parent_type == 'User':
			
		
			if MLM.objects.get(node=parent).right == None:
				MLM.objects.filter(node=parent).update(right=child)
			else:
				treesss=fetch_empty_nodes(parent)
				if treesss is not None:
					count = 0
					for userr in treesss['right']:
						if count < 1:
							right_empty=fetch_empty_nodesmlmright(userr)
							for userright in right_empty['right']:
								print(userright,'RightlllllllLLLL')
								if not MLM.objects.filter(node=userright).exists():
									MLM.objects.filter(node=userright).update(right=child)
								else:
		   							messages.warning(request, 'Already created !')
							count += 1

			if not MLM.objects.filter(node=child).exists():
				MLM.objects.create(parent=parent, node=child)
				messages.success(request, 'You have been add under '+parent.usr.first_name)
				print('RRRRRRRRRRRRRR')
			else:
				print('No node empty in RIGHT')


# ----Showing all user--------Vijay Code------------->
def fetch_empty_nodess(node):
	try:
		mlm = MLM.objects.get(node=node)
		right = fetch_one_side_empty_nodess(mlm.right, [])
		left = fetch_one_side_empty_nodess(mlm.left, [])
		return {'left':left, 'right':right}
	except MLM.DoesNotExist:
	    user = None

def fetch_one_side_empty_nodess(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None and mlm.right != None:
			members.append(node)
			fetch_one_side_empty_nodess(mlm.left, members)
			fetch_one_side_empty_nodess(mlm.right, members)
		elif mlm.right == None and mlm.left != None:
			members.append(node)
			fetch_one_side_empty_nodess(mlm.left, members)
		elif mlm.left != None and mlm.right != None:
			members.append(node)
			# members.append(mlm.node)
			fetch_one_side_empty_nodess(mlm.left, members)
			fetch_one_side_empty_nodess(mlm.right, members)
		elif mlm.left == None and mlm.right == None:
			members.append(mlm.node)
		return members
	else:
		return members

# <-------------------end code----------->

def fetch_empty_nodes(node):
	try:
		mlm = MLM.objects.get(node=node)
		left = fetch_one_side_empty_nodes(mlm.left, [])
		right = fetch_one_side_empty_nodes(mlm.right, [])
		return {'left':left, 'right':right}
	except MLM.DoesNotExist:
	    user = None

def fetch_one_side_empty_nodes(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None and mlm.right != None:
			members.append(node)
			fetch_one_side_empty_nodes(mlm.right, members)
		elif mlm.right == None and mlm.left != None:
			members.append(node)
			fetch_one_side_empty_nodes(mlm.left, members)
		elif mlm.left != None and mlm.right != None:
			fetch_one_side_empty_nodes(mlm.left, members)
			fetch_one_side_empty_nodes(mlm.right, members)
		elif mlm.left == None and mlm.right == None:
			members.append(mlm.node)
		return members
	else:
		return members

def calculate_point_value_on_order(cart):
	cartitems = CartItems.objects.filter(cart=cart)
	total_pv = 0.0
	for x in cartitems:
		pv_percent = PointValue.objects.get(category=x.product.category)
		pv = (x.total_cost/100)*pv_percent.percentage
		total_pv = total_pv + pv
	return total_pv

def fetch_nodes(node):
	try:
		mlm = MLM.objects.get(node=node)
		right = fetch_one_side_nodes(mlm.right, [])
		left = fetch_one_side_nodes(mlm.left, [])
		return {'left':left, 'right':right}
	except MLM.DoesNotExist:
		user = None
def fetch_one_side_nodes(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None and mlm.right != None:
			members.append(node)
			fetch_one_side_nodes(mlm.right, members)
		elif mlm.right == None and mlm.left != None:
			members.append(node)
			fetch_one_side_nodes(mlm.left, members)
		elif mlm.left != None and mlm.right != None:
			members.append(node)
			fetch_one_side_nodes(mlm.left, members)
			fetch_one_side_nodes(mlm.right, members)
		elif mlm.left == None and mlm.right == None:
			members.append(mlm.node)
		return members
	else:
		return members

# feching Parents of particular Node
def fetch_parent_nodes(node, parents):
	if node is not None:
		try:
			mlm = MLM.objects.get(node = node)
			if not mlm.parent.role.level.level == 'Admin':
				parents.append(mlm.parent)
				fetch_parent_nodes(mlm.parent, parents)
			return parents
		except MLM.DoesNotExist:
			user = None

	else:
		return parents

