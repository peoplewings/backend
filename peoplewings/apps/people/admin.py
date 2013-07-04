from django.contrib import admin
from models import UserProfile, Interests
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
    list_display = ('user', 'current_city')
    list_filter = ('current_city',)

    '''def user_email(self, obj):
       	return obj.user.email
    '''

class InterestsAdmin(admin.ModelAdmin):
    model = Interests
    list_display = ('gender',)
    list_filter = ('gender',)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Interests, InterestsAdmin)