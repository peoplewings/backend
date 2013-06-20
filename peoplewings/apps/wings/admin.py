from django.contrib import admin
from peoplewings.apps.wings.models import Accomodation
 
class AccomodationAdmin(admin.ModelAdmin):
       model = Accomodation
       list_display=('author','name','status','date_start','date_end')
       list_filter=('author','name','status','date_start','date_end')


admin.site.register(Accomodation, AccomodationAdmin)