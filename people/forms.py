from django import forms
from django.db import models
from django.forms import ModelForm, extras
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from people.models import UserProfile, Languages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import datetime

# Prepare birthdate year choices
now = datetime.datetime.now()
BIRTH_YEAR_CHOICES = []

for i in range(1900, now.year+1, 1):
    BIRTH_YEAR_CHOICES.append(i)

BIRTH_YEAR_CHOICES.reverse()


class RegisterForm(ModelForm):
  class Meta:
      model = UserProfile
      fields = ('birthday', 'gender')
      widgets = {
          'birthday' : extras.SelectDateWidget(years=BIRTH_YEAR_CHOICES, attrs={'class':'special'})
      }

class CustomRegisterForm(RegistrationFormUniqueEmail):
  first_name = forms.CharField(label='First name', max_length=30,required=True)
  last_name = forms.CharField(label='Last name', max_length=30, required=True)
  email_2 = forms.EmailField(label='Repeat email')
  exclude = ('username', 'password2')
  def __init__(self, *args, **kwargs):
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['first_name', 'last_name', 'email', 'email_2', 'password1', 'gender', 'birthday']
        # Trying to fix default values. Doesnt work
        #self.fields['gender'].empty_label = None
        #self.fields['gender'].widget.choices = self.fields['gender'].choices

  def clean_email_2(self):
        """
        Verifiy that the values entered into the two email fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'email' in self.cleaned_data and 'email_2' in self.cleaned_data:
            if self.cleaned_data['email'] != self.cleaned_data['email_2']:
                raise forms.ValidationError(_("The two emails fields didn't match."))
        return self.cleaned_data


# the form for EditProfile must show:
# from UserProfile: birthday, gender, interested in, civil state, languages, city, pw state, all about you,
# 					main mission, occupation, education, pw experience, personal philosophy, other pages you like,
#					people you like, favourite movies series, what you like sharing, incredible things done or seen
# 					pw opinion, political opinion, religion, quotes, people that inspired you

class CustomProfileForm(ModelForm):
  uni = forms.CharField(max_length=50, required=False)
  class Meta:
      model = UserProfile
      exclude = ('user', 'age', 'relationships', 'languages', 'universities')
      """
      widgets = {
          'universities': Textarea(attrs={'cols': 80, 'rows': 20}),
      }
      """
  def clean_uni(self):
    return self.cleaned_data['uni']

  def clean_all_about_you(self):
        """
        Verifiy the length of this field
        """
        if 'all_about_you' in self.cleaned_data:
            if len(self.cleaned_data['all_about_you']) > 250:
                raise forms.ValidationError(_("This length must be under 250 characters."))
        return self.cleaned_data['all_about_you']


class CustomAccountSettingsForm(ModelForm):
  """
  The form for EditAccountSettings must have, from User: email, first name, last name, password
  """
  class Meta:
      model = User
      fields = ('email', 'first_name', 'last_name')


 
	
def customize_register_form():
    """
    Change username label to tweak Auth based on email not username
    Embrace RegisterForm and CustomRegisterForm
    """
    AuthenticationForm.base_fields['username'].label = 'E-mail'
    CustomRegisterForm.base_fields.update(RegisterForm.base_fields)
		

customize_register_form()
