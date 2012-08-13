"""
Custom Widget classes
"""
from django.forms.widgets import Widget, Select, MultiWidget
from django import forms        
    

class DoubleSelectWidget(MultiWidget):
    """
    Custom widget to display two select fields.
    """
    def __init__(self, attrs=None, attrs2=None, choices1=None, choices2=None, mode=0):  

        _widgets = (
            Select(attrs=attrs, choices=choices1), 
            Select(attrs=attrs2, choices=choices2),
            )
        #attrs = dict(attrs1.items() + attrs2.items())
        super(DoubleSelectWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.language_id, value.level]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)

class MyMultiValueField(forms.MultiValueField):
    """
    Compress method must be implemented
    """
    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(required=True),
            forms.CharField(required=True),
        )
        #self.widget = MyMultiValueField(widgets=[fields[0].widget, fields[1].widget])
        super(MyMultiValueField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        print "data_list"
        print data_list
        if data_list: return '|'.join(data_list)