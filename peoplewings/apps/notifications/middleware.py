import re
import json

from notifications.models import NotificationsAlarm
from people.models import UserProfile
from django.contrib.auth.models import AnonymousUser

class Notification(object):

	def process_request(self, request):
		return None

	def process_response(self, request, response):	
		#import pdb; pdb.set_trace()
		compiled_regexp = re.compile("/admin/")
		if request.user and not isinstance(request.user, AnonymousUser) and not compiled_regexp.match(str(request.path_info)):
			if response.status_code == 200:		
				resp = json.loads(response.content)
				if not resp.has_key('updates'):
					resp['updates'] = {}
				try:
					prof = UserProfile.objects.get(user=request.user)
					resp['updates']['notifs'] = NotificationsAlarm.objects.filter(receiver=prof).count()
				except Exception, e:
					print 'EXCEPTION NOTIFS HEADER: ', e
					resp['updates']['notifs'] = -1
				response.content = json.dumps(resp)					
		return response