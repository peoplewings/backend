from django import forms
from django.forms import extras
from people.models import max_short_len, Language, GENDER_CHOICES
from wings.models import CAPACITY_OPTIONS
from django.forms.widgets import TextInput
from wings.forms import FUTURE_DATES

AGE_OPTIONS=[(str(i), str(i)) for i in range(18, 100)]
APPLICANT_HOST_CHOICES = [('H', 'Host'), ('A', 'Applicant')]

class SearchForm(forms.Form):
  city = forms.CharField(required=False, label="WINGS", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Where do you need accommodation?', 'class' : 'span6'}))
  start_date = forms.DateField(widget=extras.SelectDateWidget(years=FUTURE_DATES), required=False)
  end_date = forms.DateField(widget=extras.SelectDateWidget(years=FUTURE_DATES), required=False)
  capacity = forms.CharField(required=False, widget=forms.Select(choices=CAPACITY_OPTIONS))
  start_age = forms.IntegerField(label="Age", required=False, widget=forms.Select(choices=AGE_OPTIONS))
  end_age = forms.IntegerField(label="", required=False, widget=forms.Select(choices=AGE_OPTIONS))
  language = forms.CharField(required=False, max_length=max_short_len, widget=forms.Select(choices=[('','Select language')] + [(l.id, unicode(l.name)) for l in Language.objects.all()]))
  gender  = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=GENDER_CHOICES, required=False)
  applicant_host = forms.ChoiceField(widget=forms.RadioSelect, choices=APPLICANT_HOST_CHOICES, label='Looking for:', initial='H')
  city_name = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput(), label='')
