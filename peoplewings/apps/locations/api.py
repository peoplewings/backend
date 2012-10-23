from peoplewings.apps.locations.models import Country, Region, City


from tastypie.resources import ModelResource
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

class CountryResource(ModelResource):
    class Meta:
        object_class = Country
        queryset = Country.objects.all()
        allowed_methods = []
        #include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        #authorization = Authorization()
        #always_return_data = True

class RegionResource(ModelResource):
    class Meta:
        object_class = Region
        queryset = Region.objects.all()
        allowed_methods = []
        #include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        #authorization = Authorization()
        #always_return_data = True

class CityResource(ModelResource):
    class Meta:
        object_class = City
        queryset = City.objects.all()
        allowed_methods = []
        #include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        #authorization = Authorization()
        #always_return_data = True
        filtering = {
            "name": ['exact'],
        }