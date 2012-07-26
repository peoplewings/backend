from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from people.models import UserProfile
from django.contrib.auth.models import User

class RegisterForm(ModelForm):
  class Meta:
      model = UserProfile
      exclude = ('user','age','interested_in','civil_state','languages', 'city', 'pw_state', 'privacy_settings', 'relationships')  

class CustomRegisterForm(RegistrationForm):
  	first_name = forms.CharField(label='First name', max_length=30,required=True)
	last_name = forms.CharField(label='Last name', max_length=30, required=True)


AuthenticationForm.base_fields['username'].label = 'E-mail'
del CustomRegisterForm.base_fields['username']
CustomRegisterForm.base_fields.update(RegisterForm.base_fields)