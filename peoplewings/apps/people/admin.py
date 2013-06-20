from django.contrib import admin
from models import UserProfile
from django.contrib.auth.models import User
"""
class UserInLine(admin.StackedInline):
    model = User
    verbose_name = "User"
    verbose_name_plural = "Users"
    list_display = ('email',)
    fields = ('email')
"""
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = ('user', 'emails', 'current_city')
    list_filter = ('user', 'emails', 'current_city')

admin.site.register(UserProfile, UserProfileAdmin)