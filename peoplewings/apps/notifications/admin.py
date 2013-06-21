from django.contrib import admin
from models import *

class RequestsAdmin(admin.ModelAdmin):
    model = Requests
    list_display = ('receiver', 'sender', 'created', 'reference', 'read')
    list_filter = ('receiver', 'sender', 'created', 'reference', 'read')

class InvitesAdmin(admin.ModelAdmin):
    model = Invites
    list_display = ('receiver', 'sender', 'created', 'reference', 'read')
    list_filter = ('receiver', 'sender', 'created', 'reference', 'read')
    
class MessagesAdmin(admin.ModelAdmin):
    model = Messages
    list_display = ('receiver', 'sender', 'created', 'reference', 'read')
    list_filter = ('receiver', 'sender', 'created', 'reference', 'read')

admin.site.register(Requests, RequestsAdmin)
admin.site.register(Invites, InvitesAdmin)
admin.site.register(Messages, MessagesAdmin)