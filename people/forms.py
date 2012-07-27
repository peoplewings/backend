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
      exclude = ('user','age','interested_in','civil_state','languages', 'city', 'pw_state', 'privacy_settings', 
      	'relationships', 'all_about_you', 'main_mission', 'occupation', 'education', 'pw_experience', 
      	'personal_philosophy', 'other_pages_you_like', 'people_you_like', 'favourite_movies_series_others',
      	'what_you_like_sharing', 'incredible_done_seen', 'pw_opinion', 'religion', 'quotes', 'people_inspired_you')  

class CustomRegisterForm(RegistrationForm):
  	first_name = forms.CharField(label='First name', max_length=30,required=True)
	last_name = forms.CharField(label='Last name', max_length=30, required=True)


# the form for EditProfile must show:
# from UserProfile: birthday, gender, interested in, civil state, languages, city, pw state, all about you,
# 					main mission, occupation, education, pw experience, personal philosophy, other pages you like,
#					people you like, favourite movies series, what you like sharing, incredible things done or seen
# 					pw opinion, political opinion, religion, quotes, people that inspired you

class CustomProfileForm(ModelForm):
  class Meta:
      model = UserProfile
      exclude = ('user', 'age', 'relationships')

"""
The form for EditAccountSettings must have, from User: email, first name, last name, password
"""
class CustomAccountSettingsForm(ModelForm):
  class Meta:
      model = User
      fields = ('email', 'first_name', 'last_name', 'password')


AuthenticationForm.base_fields['username'].label = 'E-mail'
del CustomRegisterForm.base_fields['username']
CustomRegisterForm.base_fields.update(RegisterForm.base_fields)
