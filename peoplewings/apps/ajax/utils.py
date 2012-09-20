# AJAX helpers
from django.utils import simplejson
from django.http import HttpResponse

def json_success_response(dic):
	return json_response({
                'success': True,
                'data': dic,
                })
def json_response(x):
    return HttpResponse(simplejson.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')