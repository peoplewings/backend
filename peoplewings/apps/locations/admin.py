from django.contrib import admin
from models import *


class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ('name', 'region')
    list_filter = ('name', 'region')

class RegionAdmin(admin.ModelAdmin):
    model = Region
    list_display = ('name', 'country')
    list_filter = ('name', 'country')

class CountryAdmin(admin.ModelAdmin):
    model = Country
    list_display = ('name',)
    list_filter = ('name',)  

admin.site.register(City, CityAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Country, CountryAdmin)