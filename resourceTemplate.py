class xxxResource(ModelResource):
    
    class Meta:
        object_class = xxx
        queryset = xxx.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        include_resource_uri = False
        resource_name = 'xxx'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=xxxForm)

    def prepend_urls(self):      
        return [
            url(r"^(?P<resource_name>%s)/me%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_list_custom'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/(?P<wing_id>[\d]+)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def dispatch_list_custom(self, request, **kwargs):
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>%s)%s$" % (self._meta.resource_name, 
                self._meta.detail_uri_name, request.user.pk, trailing_slash()),
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail_custom"),
        ]
        
    def obj_get_list(self, request=None, **kwargs):
        ##GET /xxx/
        return self.create_response(request, bundle)

    def get_list(self, request=None, **kwargs):
        ##GET/xxx/me
        if 'pk' in kwargs and kwargs['pk'] == 'me':
            kwargs['pk'] = UserProfile.objects.get(user=request.user).id
        return super(UserProfileResource, self).get_list(request, **kwargs)

    def get_detail(self, request, **kwargs):
        ##GET /xxx/1
        return self.create_response(request, bundle, response_class = HttpResponse)

    def get_detail(self, request, **kwargs):
        ##GET/xxx/me
        if 'pk' in kwargs and kwargs['pk'] == 'me':
            kwargs['pk'] = UserProfile.objects.get(user=request.user).id
        return super(UserProfileResource, self).get_list(request, **kwargs)

    def obj_create(self, bundle, request, **kwargs):
        ##POST /xxx/
        return bundle

    def post_detail(self, request, **kwargs):
        ##POST /xxx/1
        return self.create_response(request, bundle, response_class = HttpResponse)
    
    def patch_detail(self, request, **kwargs):
        print 'PATCH DETAIL'        
        return self.create_response(request, {}, response_class=HttpAccepted)

    def post_detail(self, request, **kwargs):
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
            print 'PUTA MIERDA'
        print 'POST DETAIL'        
        return self.create_response(request, {}, response_class=HttpAccepted)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                varies = getattr(self._meta.cache, "varies", [])

                if varies:
                    patch_vary_headers(response, varies)             

                if request.is_ajax() and not response.has_header("Cache-Control"):
                    patch_cache_control(response, no_cache=True)

                return response
            except (BadRequest, fields.ApiFieldError), e:
                return http.HttpBadRequest(e.args[0])
            except ValidationError, e:
                return http.HttpBadRequest(', '.join(e.messages))
            except Exception, e:
                if hasattr(e, 'response'):
                    return e.response
                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise
                return self._handle_500(request, e)

        return wrapper
