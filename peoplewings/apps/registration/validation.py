from tastypie.validation import Validation

class ForgotValidation(Validation):
    
    def is_valid(self, bundle, request=None):
        """        
        for key, value in bundle.data.items():
            if 'email' in key:
                if value
        return {}
        """

