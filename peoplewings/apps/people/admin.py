from django.contrib import admin
from models import UserProfile, PhotoAlbums
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
    list_display = ('user_email', 'current_city')
    list_filter = ('current_city',)

    def user_email(self, obj):
       	return obj.user.email

class PhotoAlbumsAdmin(admin.ModelAdmin):
	model = PhotoAlbums
	list_display = ('album_id', 'author', 'name')
	list_filter = ('album_id', 'author', 'name')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PhotoAlbums, PhotoAlbumsAdmin)