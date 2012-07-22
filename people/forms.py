from django.db import models
from django.forms import ModelForm
from registration.forms import RegistrationForm
from people.models import UserProfile

class RegisterForm(ModelForm):
  class Meta:
      model = UserProfile
      exclude = ('user','age','interested_in','civil_state','languages', 'city', 'PW_state', 'privacy_settings', 'relationships')

RegistrationForm.base_fields.update(RegisterForm.base_fields)
