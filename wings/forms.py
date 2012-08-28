#forms
from wings.models import Wing
from django.forms import ModelForm
from django.forms.widgets import TextInput
from people.models import GENDER_CHOICES
from django import forms

# WINGS FORM
class WingForm(ModelForm):
  pref_gender = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=GENDER_CHOICES, required=False)
  
  hometown = forms.CharField(max_length=50, required=True, label='City')
  hometown.widget = forms.TextInput(attrs={'data-provide' : 'typeahead', 'class' : 'hometown span6'})
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  country = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
  place_id = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput(), label='')
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
      'hometown', 'postal_code', 'city_name', 'country', 'place_id']

  def clean_hometown(self):
  	return self.cleaned_data['hometown']

  def clean_city(self):
  	c = self.cleaned_data['hometown'].replace(' ', '')
  	if c == '': raise forms.ValidationError(_("You must specify your city."))
  	return self.cleaned_data['hometown']

  def clean_city_name(self):
  	if 'hometown' in self.cleaned_data:
	  	a=self.cleaned_data['hometown'].split(', ')
		if len(a) == 2:
			return a[0]
	return ''

  def clean_country(self):
  	if 'hometown' in self.cleaned_data:
	  	a=self.cleaned_data['hometown'].split(', ')
		if len(a) == 2:
			return a[1]
	return ''
