from tastypie.validation import Validation
import re

class ForgotValidation(Validation):
    
    def email_validation(self, email):
        if len(email) > 7:
		    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			    return 1
        return 0

    def contains(self, a_list, a_key):
        for items in a_list.items():
            if a_key in items: return True
        return False
        
    def is_valid(self, bundle, request=None):
        errors = {}
        ln = len(bundle.data.items())
        if ln == 1:                
            if not self.contains(bundle.data, 'email'):                                
                errors['email'] = ['This field is required']
            elif not self.email_validation(bundle.data['email']):
                    errors['email'] = ['Not a valid email']
                    print bundle.errors
        elif ln == 2:
            if not self.contains(bundle.data, 'forgot_token'):
                errors['forgot_token'] = ['This field is required']
            if not self.contains(bundle.data, 'new_password'):
                errors['new_password'] = ['This field is required']                
        else:                    
            errors['params']  = ["Bad parameters"]      
        return errors
 
        
        
        

