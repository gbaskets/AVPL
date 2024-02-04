from django import template
from main_app.models import *

register = template.Library()


@register.filter()
def binary(user):
    tree=fetch_user_tree(request.user)



@register.filter()
def check_permission(user, permission):
    if user.user_permissions.filter(codename = permission).exists():
        return True
    return False