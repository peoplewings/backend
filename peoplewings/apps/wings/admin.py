from django.contrib import admin
from peoplewings.apps.wings.models import Accomodation
from peoplewings.apps.people.models import UserProfile
from django.contrib.auth.models import User
 

class AccomodationAdmin(admin.ModelAdmin):
       model = Accomodation
       list_display=('name','author','status','date_start','date_end')
       list_filter=('name','author','status','date_start','date_end')

      

admin.site.register(Accomodation, AccomodationAdmin)