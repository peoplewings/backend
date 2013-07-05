from django.contrib import admin
from models import *
from peoplewings.apps.people.models import UserProfile
from django.contrib.auth.models import User
 

class AccomodationAdmin(admin.ModelAdmin):
	model = Accomodation
	list_display=('name','author','status','date_start','date_end')
	list_filter=('name','author','status','date_start','date_end')

class PublicTransportAdmin(admin.ModelAdmin):
	model = PublicTransport
	list_display=('name',)
	list_filter=('name',)

class WingAdmin(admin.ModelAdmin):
	model = Wing
	list_display=('name','author','status','date_start','date_end')
	list_filter=('name','author','status','date_start','date_end')
	

admin.site.register(Accomodation, AccomodationAdmin)
admin.site.register(PublicTransport, PublicTransportAdmin)
admin.site.register(Wing, WingAdmin)