from django.db import models
#from django.contrib.auth.models import User

max_short_len = 200

# COUNTRY + MANAGER
class CountryManager(models.Manager):
    def create(**kwargs):
        try:
            country = Country.objects.get(short_name=kwargs['short_name'])            
        except:
            country = Country(name=kwargs['name'], short_name=kwargs['short_name'])
            country.save()
        return country

class Country(models.Model):
    short_name = models.CharField(max_length=max_short_len, unique=True)  
    name = models.CharField(max_length=max_short_len, unique=False)
    lat = models.DecimalField(max_digits=11, decimal_places=9, default=0.0)
    lon = models.DecimalField(max_digits=12, decimal_places=9, default=0.0)
    objects = CountryManager()

# REGION +`MANAGER
class RegionManager(models.Manager):
    def create(**kwargs):
        try:
            region = Region.objects.get(short_name=kwargs['short_name'])            
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
    def create(**kwargs):
        try:
            city = City.objects.get(short_name=kwargs['short_name'])
            city.lat = kwargs['lat']
            city.lon = kwargs['lon']            
        except:
            city = City(name=kwargs['name'], short_name=kwargs['short_name'], lat=kwargs['lat'], lon=kwargs['lon'])
        city.save()
        return city

    def saveLocation(**kwargs):
    # countryN, countrySN, regionN='No region', regionSN='No region', cityN, citySN, cityLat, cityLon, locationType
        # define args
        countryN = kwargs.get('countryN', None)
        countrySN = kwargs.get('countrySN', None)
        regionN = kwargs.get('regionN', None)
        regionSN = kwargs.get('regionSN', None)
        cityN = kwargs.get('cityN', None)
        citySN = kwargs.get('citySN', None)
        cityLat = kwargs.get('cityLat', None)
        cityLon = kwargs.get('cityLon', None)
        locationType = kwargs.get('locationType', None)
        # put nulls in the args
        if regionN is None: regionN = 'No region'
        if regionSN is None: regionSN = 'No region'
        # control over the params
        if regionSN is None or countrySN is None or citySN is None: raise Exception('Invalid parameters')
        #Save the country    
        country = Country.objects.create(name=countryN, short_name=countrSN)
        countryId = country.pk
        #Save the region, if any. Else save it like "no region"
        region = Region.objects.create(name=regionN, short_name=regionSN, country = country)
        regionId = region.pk
        #Save the city
        city = City.objects.create(name=cityN, short_name=citysN, lat=cityLat, lon=cityLon, region=regionId)
        return city

class City(models.Model):
    name = models.CharField(max_length=max_short_len, unique=False)
    short_name = models.CharField(max_length=max_short_len, unique=False, default='NoName')
    lat = models.DecimalField(max_digits=11, decimal_places=9, default=0.0)
    lon = models.DecimalField(max_digits=12, decimal_places=9, default=0.0)
    region = models.ForeignKey('Region')
    objects = CityManager()
