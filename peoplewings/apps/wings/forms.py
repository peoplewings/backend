#forms

from django.forms import ModelForm, extras
from django.forms.widgets import TextInput, Textarea
from django import forms
import datetime
from django.utils.translation import ugettext_lazy as _

from peoplewings.global_vars import *
from peoplewings.apps.wings.models import Wing, Accomodation

now = datetime.datetime.now()

FUTURE_DATES = []
for i in range(now.year, now.year+5, 1):
    FUTURE_DATES.append(i)

# WINGS FORM
class WingForm(ModelForm):
  pref_gender = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), choices=PREFERRED_GENDER_CHOICES, label='Preferred gender')
  
  pets = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=PETS_CHOICES, required=False)
  transp = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TRANSPORT_CHOICES, required=False, label='Public transport')
  stat = forms.ChoiceField(required=False, widget=forms.Select(), choices=WINGS_STATUS, label='Wings status')

  wing_name = forms.CharField(max_length=50, required=False)
  city = forms.CharField(max_length=50, required=True, label='City')
  city.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'hometown span6'})
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  city_country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  city_place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput(), label='')
  class Meta:
    model = Accomodation
    exclude = ('name', 'author', 'preferred_gender', 'city', 'i_have_pet', 'pets_allowed', 'status', 'underground',
      'bus', 'tram', 'train', 'others')
    widgets = {
    	#'city' : TextInput(attrs={'data-provide': 'typeahead', 'class' : 'hometown span6'}),
      'about' : Textarea(attrs={'maxlength':max_500_char, 'size': max_500_char, 'placeholder': 'Describe your accomodation (max ' + str(max_500_char) + ' characs.)'}),
      'additional_information' : Textarea(attrs={'maxlength':max_500_char, 'size': max_500_char, 'placeholder': 'Apartment, suite, building, floor...'}),
      #'from_date' : extras.SelectDateWidget(years=FUTURE_DATES, attrs={'class':'special', 'style': 'width:120px'}),
      #'to_date' : extras.SelectDateWidget(years=FUTURE_DATES, attrs={'class':'special', 'style': 'width:120px'}),

    }


  def __init__(self, bloquear, *args, **kwargs):
      super(WingForm, self).__init__(*args, **kwargs)

      #self.fields['city'] = forms.CharField(max_length=50, required=False)
      self.fields.keyOrder = ['wing_name', 'stat', 'sharing_once', 'date_start', 'date_end', 'best_days', 'capacity', 'pref_gender',
      'wheelchair', 'where_sleeping_type', 'smoking', 'pets', 'blankets', 'live_center', 
      'transp', 'about', 'address', 'number', 'additional_information',
      'city', 'postal_code', 'city_name', 'city_country', 'city_place_id']

      if bloquear:
            self.fields['stat'].widget.attrs['disabled'] = True

class AccomodationForm(forms.Form):

    name = forms.CharField(max_length=max_short_text_len, required=True)
    status = forms.ChoiceField(choices=WINGS_STATUS, required=False)
    date_start = forms.DateField(required=False)
    date_end = forms.DateField(required=False)
    best_days = forms.ChoiceField(choices=BETTER_DAYS_CHOICES, required=False)
    is_request = forms.BooleanField(required=False)

    sharing_once = forms.BooleanField(required=False)
    capacity = forms.ChoiceField(choices=CAPACITY_OPTIONS, required=False)
    preferred_male = forms.BooleanField(required=False)
    preferred_female = forms.BooleanField(required=False)
    wheelchair = forms.BooleanField(required=False)
    where_sleeping_type = forms.ChoiceField(choices=WHERE_SLEEPING_CHOICES, required=False)
    smoking = forms.ChoiceField(choices=SMOKING_CHOICES, required=False)
    i_have_pet = forms.BooleanField(required=False)
    pets_allowed = forms.BooleanField(required=False)
    blankets = forms.BooleanField(required=False)
    live_center = forms.BooleanField(required=False)
    underground = forms.BooleanField(required=False)
    bus = forms.BooleanField(required=False)
    tram = forms.BooleanField(required=False)
    train = forms.BooleanField(required=False)
    others = forms.BooleanField(required=False)
    about = forms.CharField(max_length=max_text_msg_len, required=False)
    address = forms.CharField(max_length=max_short_text_len, required=True)
    number = forms.CharField(max_length=max_ultra_short_len, required=True)
    additional_information = forms.CharField(max_length=max_text_msg_len, required=False)   
    postal_code = forms.CharField(max_length=max_short_text_len, required=True)
    #city = forms.ForeignKey(City, on_delete=models.PROTECT)
