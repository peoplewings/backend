from django.contrib import admin
from models import *

class RequestsAdmin(admin.ModelAdmin):
    model = Requests

class InvitesAdmin(admin.ModelAdmin):
    model = Invites

class MessagesAdmin(admin.ModelAdmin):
    model = Messages

class FriendshipAdmin(admin.ModelAdmin):
    model = Friendship

admin.site.register(Requests, RequestsAdmin)
admin.site.register(Invites, InvitesAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(Friendship, FriendshipAdmin)