from peoplewings.apps.locations.models import Country, Region, City
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

from tastypie.resources import ModelResource
from tastypie import fields

class CountryResource(ModelResource):
    class Meta:
        object_class = Country
        queryset = Country.objects.all()
        allowed_methods = []
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        #authorization = Authorization()
        #always_return_data = True
        excludes = ['id']

class RegionResource(ModelResource):
    #country = fields.ToOneField(CountryResource, 'country', full=True, null=True)
    class Meta:
        object_class = Region
        queryset = Region.objects.all()
        allowed_methods = []
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        #authorization = Authorization()
        #always_return_data = True
        excludes = ['id']

class CityResource(ModelResource):
    #region = fields.ToOneField(RegionResource, 'region', full=True, null=True)
    class Meta:
        object_class = City
        queryset = City.objects.all()
        allowed_methods = []
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        #authorization = Authorization()
        #always_return_data = True
        excludes = ['id']
        filtering = {
            "name": ['exact'],
        }

