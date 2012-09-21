from django.contrib import admin
from models import Original, Cropped
import settings

class OriginalAdmin(admin.ModelAdmin):
    """
    Admin class for original image model
    """

class CroppedAdmin(admin.ModelAdmin):
    """
    Admin class for cropped image model
    """

if settings.SHOW_ADMIN:
    admin.site.register(Original, OriginalAdmin)
    admin.site.register(Cropped, CroppedAdmin)
