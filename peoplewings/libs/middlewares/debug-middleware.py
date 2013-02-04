class DebugMiddleware(object):

	def process_request(self, request):
		print 'DebugMiddleware\n'
		print request
		print '---------------------------\n'
		return None

	def process_response(self, request, response):
		return response

