from tastypie.authorization import Authorization

class ProfileAuthorization(Authorization):
    
    def apply_limits(self, request, object_list=None):
        if request and request.method in ('GET'):  # 1.
            return object_list.filter(user=request.user)
 
        if isinstance(object_list, Bundle):  # 2.
            bundle = object_list # for clarity, lets call it a bundle            
            bundle.data['user'] = {'pk': request.user.pk}  # 3.
            return bundle
 
        return []  # 4.
