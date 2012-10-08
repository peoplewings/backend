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
    short_name = models.CharField(max_length=max_short_len, unique=True)  
    name = models.CharField(max_length=max_short_len, unique=True)
    lat = models.DecimalField(max_digits=11, decimal_places=9, default=0.0)
    lon = models.DecimalField(max_digits=12, decimal_places=9, default=0.0)
    objects = CountryManager()

# REGION +`MANAGER
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
    short_name = models.CharField(max_length=max_short_len, unique=False, default='NoName')  
    lat = models.DecimalField(max_digits=11, decimal_places=9, default=0.0)
    lon = models.DecimalField(max_digits=12, decimal_places=9, default=0.0)
    country = models.ForeignKey('Country')
    objects = RegionManager()

# CITY + MANAGER
class CityManager(models.Manager):
    def create(self, **kwargs):
        try:
            city = City.objects.get(short_name=kwargs['short_name'])
            city.lat = kwargs['lat']
            city.lon = kwargs['lon']            
        except:
            city = City(name=kwargs['name'], short_name=kwargs['short_name'], lat=kwargs['lat'], lon=kwargs['lon'], region = kwargs['region'])
        city.save()
        return city

    def saveLocation(self, **kwargs):
    # countryN, countrySN, regionN='No region', regionSN='No region', cityN, citySN, cityLat, cityLon, locationType
        # define args
        countryN = kwargs.get('country_n', None)
        countrySN = kwargs.get('country_sN', None)
        regionN = kwargs.get('region_n', None)
        regionSN = kwargs.get('region_sN', None)
        cityN = kwargs.get('city_n', None)
        citySN = kwargs.get('city_sN', None)
        cityLat = kwargs.get('city_lat', None)
        cityLon = kwargs.get('city_lon', None)
        locationType = kwargs.get('location_type', None)
        # put nulls in the args
        if regionN is None: regionN = 'No region'
        if regionSN is None: regionSN = 'No region'
        # control over the params
        if regionSN is None or countrySN is None or citySN is None: raise Exception('Invalid parameters')
        #Save the country    
        country = Country.objects.create(name=countryN, short_name=countrySN)
        countryId = country.pk
        #Save the region, if any. Else save it like "no region"
        region = Region.objects.create(name=regionN, short_name=regionSN, country = country)
        regionId = region.pk
        #Save the city
        city = City.objects.create(name=cityN, short_name=citySN, lat=cityLat, lon=cityLon, region=region)
        return city

class City(models.Model):
    name = models.CharField(max_length=max_short_len, unique=False)
    short_name = models.CharField(max_length=max_short_len, unique=False, default='NoName')
    lat = models.DecimalField(max_digits=11, decimal_places=9, default=0.0)
    lon = models.DecimalField(max_digits=12, decimal_places=9, default=0.0)
    region = models.ForeignKey('Region')
    objects = CityManager()
