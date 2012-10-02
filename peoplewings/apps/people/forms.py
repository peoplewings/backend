from django import forms
from django.db import models
from django.forms import ModelForm, extras, Textarea
from django.forms.formsets import BaseFormSet
from django.forms.widgets import TextInput, Textarea
from django.contrib.auth.forms import AuthenticationForm
from peoplewings.apps.registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from models import UserProfile, Language, University, SocialNetwork, InstantMessage, max_long_len, max_short_len, max_medium_len
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import datetime

from peoplewings.global_vars import *

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

LANG_LEVEL_CHOICES = [
      ('E', 'Expert'),
    ('I', 'Intermediate'),
    ('B', 'Beginner'),
  ]


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

# 1. BASIC INFORMATION
class BasicInformationForm(ModelForm):
  interested_in = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=INTERESTED_IN_CHOICES, required=False)
  class Meta:
    model = UserProfile
    fields = ('birthday', 'show_birthday', 'gender', 'civil_state')
    widgets = {
      'birthday' : extras.SelectDateWidget(years=BIRTH_YEAR_CHOICES, attrs={'class':'special', 'style': 'width:120px'}),
    }
  def __init__(self, *args, **kwargs):
      super(BasicInformationForm, self).__init__(*args, **kwargs)
      self.fields.keyOrder = ['gender', 'birthday', 'show_birthday', 'interested_in', 'civil_state']
  

class LanguageForm(forms.Form):
  language = forms.CharField(required=True, label="Language", max_length=max_short_len, widget=forms.Select(choices=[('','Select language')] + [(l.id, unicode(l.name)) for l in Language.objects.all()]))
  level = forms.ChoiceField(required=True, label="Level", choices=[('','Select level')] + LANG_LEVEL_CHOICES)

class LanguageFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        languages = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if len(form.cleaned_data) > 0:
                lang = form.cleaned_data['language']
                if lang in languages:
                    msg = "You entered a repeated language"
                    form._errors['language'] = form.error_class([msg])
                    del form.cleaned_data["language"]
                    #raise forms.ValidationError(_("You entered a repeated language"))
                else: languages.append(lang)
            else: raise forms.ValidationError(_("This field is required"))

class UserLocationForm(forms.Form):
  hometown = forms.CharField(max_length=50, required=False)
  hometown.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'hometown span6'})
  home_city = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())
  home_country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())
  home_place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
  
  current_city = forms.CharField(max_length=50, required=False)
  current_city.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'current span6'})

  current_city_city = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())
  current_city_country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())
  current_city_place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())

class AnotherLocationForm(forms.Form):
  location = forms.CharField(max_length=50, required=False)
  location.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'hometown span6'})
  location_city = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())
  location_country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())
  location_place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())


# 2. ABOUT ME FORM
class AboutMeForm1(ModelForm):
  class Meta:
    model = UserProfile
    fields = ('all_about_you', 'main_mission', 'occupation', 'company')
    """
    all_about_you = models.TextField(max_length=max_long_len, blank=True)
    main_mission = models.TextField(max_length=max_long_len, blank=True)
    occupation = models.CharField(max_length=max_short_len, blank=True)
    company = models.CharField(max_length=max_short_len, blank=True)    
    """
    widgets = {
          'all_about_you' : Textarea(attrs={'size': max_long_len, 'placeholder': 'A description about you, can be anything'}),
          'main_mission' : Textarea(attrs={'size': max_long_len, 'placeholder' : 'What is your current mission objective. Be creative, imaginative, wacky if you need to be'}),
          'occupation' : TextInput(attrs={'size': max_short_len, 'placeholder': 'What do you do?'}),
          'company' : TextInput(attrs={'size': max_short_len, 'placeholder' : 'Where have you worked?'}),
      }

class AboutMeForm2(ModelForm):
  class Meta:
    model = UserProfile
    fields = ('personal_philosophy', 'political_opinion', 'religion')
    """
    personal_philosophy = models.TextField(max_length=max_long_len, blank=True)
    political_opinion = models.CharField(max_length=max_short_len, blank=True)
    religion = models.CharField(max_length=max_short_len, blank=True)
    """
    widgets = {
          'personal_philosophy' : Textarea(attrs={'size': max_long_len, 'placeholder': 'What is your personal phylosophy? Why live your life? Feelings? Thoughts?'}),
          'political_opinion' : TextInput(attrs={'size': max_short_len, 'placeholder': 'What are your politics?'}),
          'religion' : TextInput(attrs={'size': max_short_len, 'placeholder': 'What are your religious beliefs'}),
      }

class EducationForm(forms.Form):
  institution = forms.CharField(required=False, label="Education", max_length=max_medium_len, widget=forms.TextInput(attrs={'placeholder': 'Where have you studied?'}))
  degree = forms.CharField(required=False, label="Degree", max_length=max_short_len, widget=forms.TextInput(attrs={'placeholder': 'What have you studied?'}))
  institution.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'foo'})  

class EducationFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return


# 3. LIKES FORM
class LikesForm(ModelForm):
  class Meta:
    model = UserProfile
    fields = ('enjoy_people', 'movies',  'sports', 'other_pages', 'sharing',  'incredible', 
        'inspired_by', 'quotes', 'pw_opinion' )
    widgets = {
          'enjoy_people' : TextInput(attrs={'size': max_long_len, 'class' : 'span8', 'placeholder': 'What kind of people you like to know and learn from them'}),
          'inspired_by' : TextInput(attrs={'size': max_long_len, 'class' : 'span8'}),
          'movies' : TextInput(attrs={'size': max_long_len, 'class' : 'span8', 'placeholder': 'Movies, series, books, games...'}),
          'sports' : TextInput(attrs={'size': max_long_len, 'class' : 'span8'}),
          'other_pages' : TextInput(attrs={'size': max_long_len, 'class' : 'span8', 'placeholder': 'Other webpages and applications you like'}),
          'sharing' : TextInput(attrs={'size': max_long_len, 'class' : 'span8', 'placeholder': 'What do you like to teach, learn or share?'}),
          'incredible' : TextInput(attrs={'size': max_long_len, 'class' : 'span8', 'placeholder': 'Any amazing thing you\'ve seen or done in your life'}),
          'quotes' : Textarea(attrs={'size': max_long_len, 'class' : 'span8', 'rows' : 4}),
          'pw_opinion' : TextInput(attrs={'size': max_long_len, 'class' : 'span8', 'placeholder': 'Your opinion about PEOPLEWINGS'}),
      }  


# 4. CONTACT INFORMATION FORM
class ContactInformationForm(ModelForm):
  
  class Meta:
    model = UserProfile
    fields = ('emails', 'phone')

  def clean_phone(self):
    if 'phone' in self.cleaned_data:
      value = self.cleaned_data['phone']
      if value == '': return ''
      try:
        v = int(value)
      except:
        raise forms.ValidationError(_("This field must be an integer"))
      return v
      
class SocialNetworkForm(forms.Form):
  social_network = forms.CharField(required=False, label="Social Network", max_length=max_short_len, widget=forms.Select(choices=[(l.id, unicode(l.name)) for l in SocialNetwork.objects.all()]))
  social_network_username = forms.CharField(required=False, label="Social Network Username", max_length=max_short_len, widget=forms.TextInput(attrs={'placeholder': 'Username or public profile link'}))

class SocialNetworkFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        social_networks = []
        social_networks_usernames = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            social = form.cleaned_data['social_network']
            username = form.cleaned_data['social_network_username']

            for i in range(len(social_networks)):
              if social == social_networks[i] and username == social_networks_usernames[i]:
                msg = "You already specified this username fot the same social network"
                form._errors['social_network_username'] = form.error_class([msg])
                del form.cleaned_data["social_network_username"]
                #raise forms.ValidationError(_("You entered a repeated social network"))
            social_networks.append(social)
            social_networks_usernames.append(username)


class InstantMessageForm(forms.Form):
  instant_message = forms.CharField(required=False, label="Instant Message", max_length=max_short_len, widget=forms.Select(choices=[(l.id, unicode(l.name)) for l in InstantMessage.objects.all()]))
  instant_message_username = forms.CharField(required=False, label="Instant Message Username", max_length=max_short_len, widget=forms.TextInput(attrs={'placeholder': 'Username'}))

class InstantMessageFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        ims = []
        instant_message_usernames = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i] 
            im = form.cleaned_data['instant_message']
            username = form.cleaned_data['instant_message_username']

            for i in range(len(ims)):
              if im == ims[i] and username == instant_message_usernames[i]:
                msg = "You already specified this username for the same instant message"
                form._errors['instant_message_username'] = form.error_class([msg])
                del form.cleaned_data["instant_message_username"]
                #raise forms.ValidationError(_("You entered a repeated instant message"))
            ims.append(im)
            instant_message_usernames.append(username)


# CUSTOM PROFILE FORM
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


class StatusForm(ModelForm):
  class Meta:
    model=UserProfile
    fields = ('pw_state', )


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

### New Forms ####

class UserProfileForm(forms.Form):
    pw_state = forms.ChoiceField(choices=PW_STATE_CHOICES, required=False)
    avatar = forms.CharField(max_length=1, required=False)

    #Basic Information
    """
    birthday_day = forms.IntegerField(min_value=1, max_value=31, required=False)
    birthday_month = forms.IntegerField(min_value=1, max_value=12, required=False)
    birthday_year = forms.IntegerField(min_value=1900, max_value=2100, required=False)

    show_birthday = forms.CharField(max_length=1, choices=BIRTHDAY_CHOICES)
    gender = forms.CharField(max_length=1, choices=GENDER_CHOICES)
    interested_in = forms.CharField(max_length=1)
    civil_state = forms.CharField(max_length=2, choices=CIVIL_STATE_CHOICES)
    #languages = forms.ManyToManyField(Language, through='UserLanguage', null=True)
    # Locations
    #current_city = forms.ForeignKey(City, related_name='cc+', null=True)
    #hometown = forms.ForeignKey(City, related_name='ht+', null=True)
    #other_locations = forms.ManyToManyField(City, related_name='ol+', null=True)

    # Contact info

    emails = forms.EmailField()
    phone = forms.CharField(max_length=max_short_len, blank=True)
    social_networks = forms.ManyToManyField(SocialNetwork, through='UserSocialNetwork')
    instant_messages = forms.ManyToManyField(InstantMessage, through='UserInstantMessage')

    # About me
    all_about_you = forms.TextField(max_length=max_long_len, blank=True)
    main_mission = forms.TextField(max_length=max_long_len, blank=True, verbose_name='Current mission')
    occupation = forms.CharField(max_length=max_short_len, blank=True)
    company = forms.CharField(max_length=max_short_len, blank=True, verbose_name='Companies')
    universities = forms.ManyToManyField(University, through='UserProfileStudiedUniversity')
    personal_philosophy = forms.TextField(max_length=max_long_len, blank=True)
    political_opinion = forms.CharField(max_length=max_short_len, blank=True, verbose_name='Political views')
    religion = forms.CharField(max_length=max_short_len, blank=True)

    # Likes
    enjoy_people = forms.TextField(verbose_name="People I enjoy", max_length=max_long_len, blank=True)
    # peliculas, libros, series, videojuegos, musica
    movies = forms.TextField(verbose_name="Likes", max_length=max_long_len, blank=True)
    # deportes y actividades favoritas
    sports = forms.TextField(max_length=max_long_len, blank=True)
    other_pages = forms.TextField(verbose_name="Likes", max_length=max_long_len, blank=True)    
    # que te gusta compartir o ensenyar
    sharing = forms.TextField(verbose_name="Show, learn, share...", max_length=max_long_len, blank=True)
    # cosas increibles que hayas hecho o visto
    incredible = forms.TextField(verbose_name="Amazing things done/seen", max_length=max_long_len, blank=True)
    inspired_by = forms.TextField(verbose_name="People who inspires you", max_length=max_long_len, blank=True)
    # citas
    quotes = forms.TextField(verbose_name="Favorite quotations", max_length=max_long_len, blank=True)
    # opinion sobre peoplewings
    pw_opinion = forms.TextField(verbose_name="Your opinion please", max_length=max_long_len, blank=True) 

    # Trips
    places_lived_in = forms.TextField(max_length=max_long_len, blank=True)
    places_visited = forms.TextField(max_length=max_long_len, blank=True)    
    places_gonna_go = forms.TextField(max_length=max_long_len, blank=True)
    places_wanna_go = forms.TextField(max_length=max_long_len, blank=True) 





    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.CharField(max_length=50, required=True)
    email_2 = forms.CharField(max_length=50, required=True)
    birthday_day = forms.IntegerField(min_value=1, max_value=31, required=True)
    birthday_month = forms.IntegerField(min_value=1, max_value=12, required=True)
    birthday_year = forms.IntegerField(min_value=1900, max_value=2100, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    password1 = forms.CharField(max_length=50, required=True)
    """
