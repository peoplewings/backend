from django.contrib import admin
from models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
	model = Feedback
	list_display = ('user','date','browser')
	list_filter = ('user','date','browser')
    
admin.site.register(Feedback, FeedbackAdmin)