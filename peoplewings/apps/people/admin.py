from django.contrib import admin
from models import UserProfile, PhotoAlbums, Photos
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
    list_display = ('author', 'name')
    list_filter = ('author', 'name')

class PhotosAdmin(admin.ModelAdmin):
    model = Photos
    list_display = ('author', 'album', 'photo_hash')
    list_filter = ('author', 'album', 'photo_hash')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PhotoAlbums, PhotoAlbumsAdmin)
admin.site.register(Photos, PhotosAdmin)