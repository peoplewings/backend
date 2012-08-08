"""
Custom Widget classes
"""

from django.forms.widgets import Widget, Select, MultiWidget


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
            return [value.choice1, value.choice2]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)