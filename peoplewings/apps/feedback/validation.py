from tastypie.validation import Validation
import re

class FeedbackValidation(Validation):

    def is_valid(self, bundle, request=None):
        errors = {}
        for key, value in bundle.data.items():
            if key == 'text':
                if value == '':
                    errors['text'] = ['Empty field is not allowed']
                else:
                    if len(value) > 500: errors['text'] = ['Not a valid field']
            elif key == 'ftype':
                if value == '':
                    errors['ftype'] = ['Empty field is not allowed']
        return errors
        

