import re
import json

from notifications.models import NotificationsAlarm
from people.models import UserProfile
from django.contrib.auth.models import AnonymousUser

class Crop(object):

	def process_request(self, request):
		return None

	def process_response(self, request, response):		
		if request.user and not isinstance(request.user, AnonymousUser):
			if response.status_code == 200:		
				resp = json.loads(response.content)
				try:
					prof = UserProfile.objects.get(user=request.user)
					if not resp.has_key('updates'):
						resp['updates'] = {}
					big_avatar = prof.avatar.split('/')[len(prof.avatar.split('/'))]
					small_avatar = prof.thumb_avatar.split('/')[len(prof.thumb_avatar.split('/'))]
					if big_avatar == small_avatar and prof.avatar_updated==True:
						resp['updates']['avatar'] = True
						prof.avatar_updated = False
						prof.save()
					else:
						resp['updates']['avatar'] = False
				response.content = json.dumps(resp)					
		return response
