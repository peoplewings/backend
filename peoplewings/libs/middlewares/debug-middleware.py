from django.conf import settings
import logging
import json
import datetime

class DebugMiddleware(object):

	def process_request(self, request):	
		return None

	def log_fine(self, request, response):
		today = datetime.datetime.today()
		log_date = '%s-%s-%s' % (today.day, today.month, today.year)
		logging.basicConfig(filename='log/%s.log' % log_date, format='%(asctime)s  %(levelname)s  %(message)s', level=logging.INFO)
		token = getattr(request.META, 'HTTP_X_AUTH_TOKEN', 'NO_TOKEN')
		content = json.loads(response.content)
		post_params = request.raw_post_data
		get_params = json.dumps(request.GET)
		
		if content.has_key('status'):
			if content['status'] == False:
				if content.has_key('errors'):
					for i in content['errors']:
						logging.error('%s %s %s %s %s %s' % (request.META['REQUEST_METHOD'], request.META['PATH_INFO'], token, i["type"], get_params, post_params))
				else:
					logging.critical('%s %s %s %s' % (request.META['REQUEST_METHOD'], request.META['PATH_INFO'], token, 'NO_ERRORS_FIELD'))
			else:
				logging.info('%s %s %s %s' % (request.META['REQUEST_METHOD'], request.META['PATH_INFO'], token, 'OK'))
		else:
			logging.critical('%s %s %s %s' % (request.META['REQUEST_METHOD'], request.META['PATH_INFO'], token, 'NO_STATUS_FIELD'))

	def process_response(self, request, response):		
		debug = getattr(settings, 'DEBUG', False)
		if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' not in request.META:		
			if debug:
				#Debug == True. We will only log bad requests
				self.log_fine(request, response)
			else:
				#Debug != False. We log AND take out the content of the response
				self.log_fine(request, response)
				content = json.loads(response.content)
				if content.has_key('status'):
					if content['status'] == False:
						errors = []
						errors_allowed = ["EMAIL_IN_USE", "AUTH_REQUIRED", "USED_KEY", "EXPIRED_KEY", "INVALID_USER_OR_PASS", "INACTIVE_USER", "AUTH_REQUIRED"]
						if content.has_key('errors'):
							for i in content['errors']:
								if i['type'] in errors_allowed:
									errors.append(i)
						response.content = json.dumps({"status":False, "errors": errors})

		return response

