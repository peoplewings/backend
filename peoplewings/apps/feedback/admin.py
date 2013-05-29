from django.contrib import admin
from models import Feedback
from django.contrib.auth.models import User
"""
class UserInLine(admin.StackedInline):
    model = User
    verbose_name = "User"
    verbose_name_plural = "Users"
    list_display = ('email',)
    fields = ('email')
"""
class FeedbackAdmin(admin.ModelAdmin):
    model = Feedback
    list_display = ('user', 'date', 'browser', 'ftype')
    fields =  ('user', 'date', 'browser', 'ftype', 'text')
    readonly_fields = ("date",)

admin.site.register(Feedback, FeedbackAdmin)