from django.contrib import admin
from models import UserProfile
from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.models import User

'''
class UserInLine(admin.StackedInline):
    model = User
    verbose_name = "User"
    verbose_name_plural = "Users"
    list_display = ('email',)
    fields = ('email')
'''

class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = ('user', 'current_city')
    list_filter = ('user','current_city',)

    '''
    def user_email(self, obj):
       	return obj.user.email
    '''

admin.site.register(UserProfile, UserProfileAdmin)