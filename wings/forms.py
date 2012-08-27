#forms
from wings.models import Wing
from django.forms import ModelForm
from django.forms.widgets import TextInput

# WINGS FORM
class WingForm(ModelForm):
  class Meta:
    model = Wing
    exclude = ('author')
    widgets = {
    	'city' : TextInput(attrs={'data-provide': 'typeahead', 'class' : 'hometown span6'}),
  	}

