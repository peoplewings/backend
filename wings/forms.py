#forms
from wings.models import Wing
from django.forms import ModelForm
from django.forms.widgets import TextInput
from people.models import GENDER_CHOICES
from django import forms

# WINGS FORM
class WingForm(ModelForm):
  pref_gender = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=GENDER_CHOICES, required=False)
  
  city = forms.CharField(max_length=50, required=True, label='City')
  city.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'hometown span6'})
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  city_country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  city_place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput(), label='')
  class Meta:
    model = Wing
    exclude = ('author', 'preferred_gender', 'city')
    widgets = {
    	#'city' : TextInput(attrs={'data-provide': 'typeahead', 'class' : 'hometown span6'}),
        #'place_id': forms.HiddenInput(),
  	}

  def __init__(self, *args, **kwargs):
      super(WingForm, self).__init__(*args, **kwargs)
      #self.fields['city'] = forms.CharField(max_length=50, required=False)
      self.fields.keyOrder = ['name', 'status', 'sharing_once', 'from_date', 'to_date', 'better_days', 'capacity', 'pref_gender',
      'wheelchair', 'where_sleeping_type', 'smoking', 'i_have_pet', 'pets_allowed', 'blankets', 'live_center', 
      'underground', 'bus', 'tram', 'train', 'others', 'about', 'address', 'number', 'additional_information',
      'city', 'postal_code', 'city_name', 'city_country', 'city_place_id']
