
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm,PasswordResetForm,AuthenticationForm
# from django import forms
# from django.forms import EmailField,TextInput,PasswordInput,ImageField

# from .models import *

# class AboutForm(forms.ModelForm):
#     class Meta:
#         model = AboutUs
#         fields = '__all__'



# class Users_Form(forms.ModelForm):
   
#     class Meta:
#         model=User
#         fields =  '__all__'
#         exclude = ('password','last_login','is_superuser','groups', 'date_joined')


# class Staffs_User_Form(forms.ModelForm):
   
#     class Meta:
#         model=Staffs_User
#         fields =  '__all__'
#         exclude = ('user',)

# class StaffCreationForm(forms.ModelForm):
#     class Meta:
       
#         model = User
#         fields = ['first_name' , 'last_name' , 'email' ,'password','is_active', 'is_staff',]
#         email = forms.EmailField(required=True, max_length=100)

