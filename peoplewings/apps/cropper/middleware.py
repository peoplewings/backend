import re
import json

from notifications.models import NotificationsAlarm
from people.models import UserProfile
from django.contrib.auth.models import AnonymousUser

class Crop(object):

	def process_request(self, request):
		return None

	def process_response(self, request, response):	
		#import pdb; pdb.set_trace()	
		compiled_regexp = re.compile("/admin/")
		if request.user and not isinstance(request.user, AnonymousUser) and not compiled_regexp.match(str(request.path_info)):
			if response.status_code == 200:		
				resp = json.loads(response.content)
				try:
					prof = UserProfile.objects.get(user=request.user)
					if not resp.has_key('updates'):
						resp['updates'] = {}
					big_avatar = prof.avatar.split('/')[len(prof.avatar.split('/'))-1]
					small_avatar = prof.thumb_avatar.split('/')[len(prof.thumb_avatar.split('/'))-1]
					if big_avatar == small_avatar and prof.avatar_updated==True:
						resp['updates']['avatar'] = True
						prof.avatar_updated = False
						prof.save()
					else:
						resp['updates']['avatar'] = False
					response.content = json.dumps(resp)
				except:
					response.content = json.dumps(resp)					
		return response
