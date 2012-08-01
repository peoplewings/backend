from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from people.models import UserProfile, Languages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class RegisterForm(ModelForm):
  class Meta:
      model = UserProfile
      fields = ('birthday', 'gender')
      
      """
      exclude = ('user','age','interested_in','civil_state','languages', 'city', 'pw_state', 'privacy_settings', 
      	'relationships', 'all_about_you', 'main_mission', 'occupation', 'education', 'pw_experience', 
      	'personal_philosophy', 'other_pages_you_like', 'people_you_like', 'favourite_movies_series_others',
      	'what_you_like_sharing', 'incredible_done_seen', 'pw_opinion', 'political_opinion', 'religion', 'quotes', 'people_inspired_you')  
		"""

class CustomRegisterForm(RegistrationFormUniqueEmail):
  first_name = forms.CharField(label='First name', max_length=30,required=True)
  last_name = forms.CharField(label='Last name', max_length=30, required=True)
  email_2 = forms.EmailField(label='Repeat email')
  def __init__(self, *args, **kwargs):
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['first_name', 'last_name', 'email', 'email_2', 'password1', 'gender', 'birthday']

  def clean(self):
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

LANGUAGES_CHOICES = (
        ('E', 'English'),
        ('G', 'German'),
        ('S', 'Spanish'),
    )


class CustomProfileForm(ModelForm):
  #lang = forms.MultipleChoiceField(required=False, choices=LANGUAGES_CHOICES , widget=forms.CheckboxSelectMultiple)
  class Meta:
      model = UserProfile
      exclude = ('user', 'age', 'relationships', 'languages')

      #field = ('lang')

  def clean_all_about_you(self):
        """
        Verifiy the length of this field
        """
        if 'all_about_you' in self.cleaned_data:
            if len(self.cleaned_data['all_about_you']) > 2:
                raise forms.ValidationError(_("This length must be under 250 characters."))
        return self.cleaned_data['all_about_you']

"""
The form for EditAccountSettings must have, from User: email, first name, last name, password
"""
class CustomAccountSettingsForm(ModelForm):
  class Meta:
      model = User
      fields = ('email', 'first_name', 'last_name')


def customize_register_form():
    AuthenticationForm.base_fields['username'].label = 'E-mail'
    RegisterForm.base_fields['birthday'].label = 'Date of birth'
    CustomProfileForm.base_fields['universities'].widget = forms.TextInput()
    del CustomRegisterForm.base_fields['username']
    del CustomRegisterForm.base_fields['password2']
    CustomRegisterForm.base_fields.update(RegisterForm.base_fields)
	

customize_register_form()
