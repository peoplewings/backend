import re
import json

from people.models import Photos as PhotosModel, UserProfile
from django.contrib.auth.models import AnonymousUser

class Photos(object):

	def process_request(self, request):
		return None

	def process_response(self, request, response):	
		#import pdb; pdb.set_trace()	
		compiled_regexp = re.compile("/admin/")
		if request.user and not isinstance(request.user, AnonymousUser) and not compiled_regexp.match(str(request.path_info)):
			if response.status_code == 200:		
				resp = json.loads(response.content)
				try:
					photos = PhotosModel.objects.filter(author=UserProfile.objects.get(user=request.user)).filter(add_notificated=False)				
					if not resp.has_key('updates'):
						resp['updates'] = {}
					resp['updates']['photos'] = []
					for i in photos:				
						resp['updates']['photos'].append(i.pk)
						i.add_notificated = True
						i.save()

					response.content = json.dumps(resp)
				except:
					response.content = json.dumps(resp)					
		return response
