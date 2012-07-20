from django.db import models
from django.forms import ModelForm
from people.models import UserProfile
 
class ProfileForm(ModelForm):
  class Meta:
      model = User
      # exclude = ('field1','field2','field3',)