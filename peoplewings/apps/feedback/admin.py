from django.contrib import admin
from models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
	model = Feedback
	list_display = ('user','date','browser','ftype')
	list_filter = ('user','date','browser','ftype')
    
admin.site.register(Feedback, FeedbackAdmin)