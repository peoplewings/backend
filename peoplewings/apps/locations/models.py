from django.db import models
#from django.contrib.auth.models import User

max_short_len = 200

# COUNTRY + MANAGER
class CountryManager(models.Manager):
    def create(self, **kwargs):
        try:
            country = Country.objects.get(short_name=kwargs['short_name'])            
        except:
            country = Country(name=kwargs['name'], short_name=kwargs['short_name'])
            country.save()
        return country

class Country(models.Model):
    name = models.CharField(max_length=max_short_len, unique=True)
    objects = CountryManager()

# REGION + MANAGER
class RegionManager(models.Manager):
    def create(self, **kwargs):
        try:
            region = Region.objects.get(short_name=kwargs['short_name'], country=kwargs['country'])            
        except:
            region = Region(name=kwargs['name'], short_name=kwargs['short_name'], country=kwargs['country'])
            region.save()
        return region

class Region(models.Model):
    name = models.CharField(max_length=max_short_len, unique=False, default='NoName')
    country = models.ForeignKey('Country')
    objects = RegionManager()

# CITY + MANAGER
class CityManager(models.Manager):
    
    def get_or_create(self, **kwargs):
        try:
            city = City.objects.get(name=kwargs['name'], region=kwargs['region'])
            city.lat = kwargs['lat']
            city.lon = kwargs['lon']            
        except Exception, e:
            print 'city.get_or_create ', e
            city = City(name=kwargs['name'], lat=kwargs['lat'], lon=kwargs['lon'], region = kwargs['region'])
        city.save()
        return city
    

    def saveLocation(self, **kwargs):
    # countryN, countrySN, regionN='No region', regionSN='No region', cityN, citySN, cityLat, cityLon, locationType
        # define args        
        countryN = kwargs.get('country', None)
        regionN = kwargs.get('region', 'NoName')
        cityN = kwargs.get('name', None)
        cityLat = kwargs.get('lat', None)
        cityLon = kwargs.get('lon', None)
        #locationType = kwargs.get('location_type', None)
        # put nulls in the args
        # control over the params
        #if regionSN is None or countrySN is None or citySN is None: raise Exception('Invalid parameters')        
        try:
            #Save the country  
            country, b = Country.objects.get_or_create(name=countryN)            
            #Save the region, if any. Else save it like "no region"
            region, b = Region.objects.get_or_create(name=regionN, country = country)
            #Save the city
            city = City.objects.get_or_create(name=cityN, lat=cityLat, lon=cityLon, region=region)         
            return city
        except Exception, e: 
            print e
            return None    

class City(models.Model):
    name = models.CharField(max_length=max_short_len, unique=False)
    lat = models.DecimalField(max_digits=11, decimal_places=9, default=0.0)
    lon = models.DecimalField(max_digits=12, decimal_places=9, default=0.0)
    region = models.ForeignKey('Region')
    objects = CityManager()

    def stringify(self):
        return '%s, %s, %s' % (self.name, self.region.name, self.region.country.name)
