#forms
from wings.models import Wing, max_500_char
from django.forms import ModelForm
from django.forms.widgets import TextInput, Textarea
from people.models import max_long_len, PW_STATE_CHOICES
from django import forms

WINGS_STATUS = list(PW_STATE_CHOICES)
WINGS_STATUS.pop()

GENDER_CHOICES = (
    ('W', 'Woman'),
    ('M', 'Man'),
)

PETS_CHOICES = (
(0, 'I have pet'),
(1, 'Guests pets allowed'),
)

TRANSPORT_CHOICES = (
(0, 'Underground'),
(1, 'Bus'),
(2, 'Tram'),
(3, 'Train'),
(4, 'Others'),
)

# WINGS FORM
class WingForm(ModelForm):
  pref_gender = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=GENDER_CHOICES, required=False, label='Preferred gender')
  
  pets = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=PETS_CHOICES, required=False)
  transp = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TRANSPORT_CHOICES, required=False, label='Public transport')
  stat = forms.ChoiceField(required=False, choices=WINGS_STATUS, label='Wings status', widget=forms.Select())

  city = forms.CharField(max_length=50, required=True, label='City')
  city.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'hometown span6'})
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  city_country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  city_place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput(), label='')
  class Meta:
    model = Wing
    exclude = ('author', 'preferred_gender', 'city', 'i_have_pet', 'pets_allowed', 'status', 'underground',
      'bus', 'tram', 'train', 'others')
    widgets = {
    	#'city' : TextInput(attrs={'data-provide': 'typeahead', 'class' : 'hometown span6'}),
      'about' : Textarea(attrs={'maxlength':max_500_char, 'size': max_500_char, 'placeholder': 'Describe your accomodation (max ' + str(max_500_char) + ' characs.)'}),
      'additional_information' : Textarea(attrs={'maxlength':max_500_char, 'size': max_500_char, 'placeholder': 'Add more information about your host (max ' + str(max_500_char) + ' characs.)'}),
  	}

  def __init__(self, bloquear, *args, **kwargs):
      super(WingForm, self).__init__(*args, **kwargs)

      #self.fields['city'] = forms.CharField(max_length=50, required=False)
      self.fields.keyOrder = ['name', 'stat', 'sharing_once', 'from_date', 'to_date', 'better_days', 'capacity', 'pref_gender',
      'wheelchair', 'where_sleeping_type', 'smoking', 'pets', 'blankets', 'live_center', 
      'transp', 'about', 'address', 'number', 'additional_information',
      'city', 'postal_code', 'city_name', 'city_country', 'city_place_id']

      if bloquear:
            self.fields['stat'].widget.attrs['disabled'] = True
  


