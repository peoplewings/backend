from django import forms
from django.db import models
from django.forms import ModelForm, extras, Textarea
from django.forms.formsets import BaseFormSet
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from people.models import UserProfile, Language, University, max_long_len, max_short_len
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from people.widgets import DoubleSelectWidget, MyMultiValueField

import datetime

# Prepare birthdate year choices
now = datetime.datetime.now()
BIRTH_YEAR_CHOICES = []

for i in range(1900, now.year-5, 1):
    BIRTH_YEAR_CHOICES.append(i)

BIRTH_YEAR_CHOICES.reverse()

INTERESTED_IN_CHOICES = (
      ('M', 'Male'),
	  ('F', 'Female'),
  )

LANG_LEVEL_CHOICES = (
      ('E', 'Expert'),
	  ('I', 'Intermediate'),
	  ('B', 'Beginner'),
  )


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

  def clean_email_2(self):
        """
        Verifiy that the values entered into the two email fields match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'email' in self.cleaned_data and 'email_2' in self.cleaned_data:
            if self.cleaned_data['email'] != self.cleaned_data['email_2']:
                raise forms.ValidationError(_("The two emails fields didn't match."))
        return self.cleaned_data['email_2']



class BasicInformationForm(ModelForm):
  interested_in = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=INTERESTED_IN_CHOICES, required=False)
  class Meta:
    model = UserProfile
    fields = ('birthday', 'show_birthday', 'gender', 'civil_state')  #'interested_in',
    widgets = {
      'birthday' : extras.SelectDateWidget(years=BIRTH_YEAR_CHOICES, attrs={'class':'special'}),
    }
  def __init__(self, *args, **kwargs):
      super(BasicInformationForm, self).__init__(*args, **kwargs)
      self.fields.keyOrder = ['gender', 'birthday', 'show_birthday', 'interested_in', 'civil_state']
	

class LanguageForm(forms.Form):
  language = forms.CharField(required=False, label="Languages", max_length=max_short_len, widget=forms.Select(choices=[(l.id, unicode(l.name)) for l in Language.objects.all()]))
  level = forms.ChoiceField(required=False, label="Level", choices=LANG_LEVEL_CHOICES)
  #languages = MyMultiValueField(required=False, label="Languages", widget=DoubleSelectWidget(attrs2={'style' : 'margin-left: 20px'}, choices1=[(l.id, unicode(l.name)) for l in Language.objects.all()], choices2=LANG_LEVEL_CHOICES))
  def clean_language(self):
      if 'language' in self.cleaned_data:
          return self.cleaned_data['language']
      
  def clean_level(self):
      if 'level' in self.cleaned_data:
          return self.cleaned_data['level']

class LanguageFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        languages = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            lang = form.cleaned_data['language']
            if lang in languages:
                raise forms.ValidationError(_("You entered a repeated language"))
            languages.append(lang)

class CustomProfileForm(ModelForm):
  uni = forms.CharField(max_length=50, required=False)
  uni.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'foo'})
  class Meta:
      model = UserProfile
      exclude = ('user', 'age', 'relationships', 'languages', 'universities')
      widgets = {
          'birthday' : extras.SelectDateWidget(years=BIRTH_YEAR_CHOICES, attrs={'class':'special'}),
          #'universities': Textarea(attrs={'cols': 80, 'rows': 20}),
      }

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

  def clean_gender(self):
        """
        Verifiy that gender is either Male or Female
        """
        if 'gender' in self.cleaned_data:
            if self.cleaned_data['gender'] not in ('M', 'F'):
                raise forms.ValidationError(_("Please select a gender."))
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
    Change username label to tweak Auth based on email not username. Embrace RegisterForm and CustomRegisterForm
    """
    AuthenticationForm.base_fields['username'].label = 'E-mail'
    CustomRegisterForm.base_fields.update(RegisterForm.base_fields)
		

customize_register_form()