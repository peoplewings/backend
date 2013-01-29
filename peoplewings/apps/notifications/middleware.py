import re
import json

from notifications.models import NotificationsAlarm
from people.models import UserProfile
from django.contrib.auth.models import AnonymousUser

class Notification(object):

	def process_request(self, request):

		return None

	def process_response(self, request, response):
		if request.user and not isinstance(request.user, AnonymousUser):
			if response.status_code == 200:		
				resp = json.loads(response.content)
				prof = UserProfile.objects.get(user=request.user)
				resp['updates'] = {}
				resp['updates']['notifs'] = NotificationsAlarm.objects.filter(receiver=prof).count()
				response.content = json.dumps(resp)					
		return response

