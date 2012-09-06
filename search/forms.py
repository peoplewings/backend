from django import forms
from django.forms import extras
from people.models import max_short_len, Language
from people.forms import LANG_LEVEL_CHOICES
from wings.models import CAPACITY_OPTIONS, BETTER_DAYS_CHOICES
from wings.forms import WINGS_STATUS, TRANSPORT_CHOICES, PREFERRED_GENDER_CHOICES
from django.forms.widgets import TextInput
from wings.forms import FUTURE_DATES

AGE_OPTIONS=[(str(i), str(i)) for i in range(18, 91)]
APPLICANT_HOST_CHOICES = [('H', 'Host'), ('A', 'Applicant')]


SEARCH_SMOKING_CHOICES = (
    ('A', 'Smoking allowed'),
    ('N', 'Host is non smoker'),
)

SEARCH_PETS_CHOICES = (
    ('N', 'Host has no pets'),
    ('A', 'Pets allowed'),
)

LOCAL_TRAVELER_CHOICES = (
    ('L', 'Local'),
    ('T', 'Traveler'),
)

class SearchForm(forms.Form):
  wings = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='WINGS')
  city = forms.CharField(required=False, label='', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Where do you need accommodation?', 'class' : 'span6'}))
  start_date = forms.DateField(required=False)
  end_date = forms.DateField(required=False)
  capacity = forms.CharField(required=False, widget=forms.Select(choices=CAPACITY_OPTIONS))
  people = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='PEOPLE')
  start_age = forms.IntegerField(label="Age", required=False, widget=forms.Select(choices=AGE_OPTIONS))
  end_age = forms.IntegerField(label="", required=False, widget=forms.Select(choices=AGE_OPTIONS), initial='90')
  language = forms.CharField(required=False, max_length=max_short_len, widget=forms.Select(choices=[('','All')] + [(l.id, unicode(l.name)) for l in Language.objects.all()]))
  gender  = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=PREFERRED_GENDER_CHOICES, required=False, label='')
  applicant_host = forms.ChoiceField(widget=forms.RadioSelect, choices=APPLICANT_HOST_CHOICES, label='', initial='H')
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')

class WingBasicForm(forms.Form):
  city = forms.CharField(required=False, label='WINGS', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Where do you need accommodation?', 'class' : 'span6'}))
  start_date = forms.DateField(required=False)
  end_date = forms.DateField(required=False)
  capacity = forms.CharField(required=False, widget=forms.Select(choices=CAPACITY_OPTIONS))

class PeopleBasicForm(forms.Form):
  people = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='PEOPLE')
  start_age = forms.IntegerField(label="Age", required=False, widget=forms.Select(choices=AGE_OPTIONS))
  end_age = forms.IntegerField(label="", required=False, widget=forms.Select(choices=AGE_OPTIONS), initial='90')
  language = forms.CharField(initial=['M', 'F'], required=False, max_length=max_short_len, widget=forms.Select(choices=[('','All')] + [(l.id, unicode(l.name)) for l in Language.objects.all()]))
  gender  = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=PREFERRED_GENDER_CHOICES, required=False, label='')
  applicant_host = forms.ChoiceField(widget=forms.RadioSelect, choices=APPLICANT_HOST_CHOICES, label='', initial='H')
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')

class WingAdvancedForm(forms.Form):
  wings_advanced = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='WINGS Advanced')
  wings_status = forms.CharField(required=False, widget=forms.Select(choices=WINGS_STATUS))
  better_days = forms.CharField(required=False, widget=forms.Select(choices=BETTER_DAYS_CHOICES), label='Better days to host')
  public_transport = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TRANSPORT_CHOICES, required=False)
  smoking = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(choices=SEARCH_SMOKING_CHOICES))
  pets  = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=SEARCH_PETS_CHOICES, required=False, label='')
  live_center = forms.ChoiceField(initial=False)
  wheelchair_accessible = forms.ChoiceField(initial=False)

class PeopleAdvancedForm(forms.Form):
  people_advanced = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='PEOPLE Advanced')
  language_level = forms.CharField(required=False, max_length=max_short_len, widget=forms.Select(choices=LANG_LEVEL_CHOICES))
  local_traveler = forms.CharField(required=False, max_length=max_short_len, widget=forms.Select(choices=LOCAL_TRAVELER_CHOICES))

