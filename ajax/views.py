# Create your views here.
from people.models import University
import json
from django.http import HttpResponse
from django.db.models import Q

def searchUniversity(request):
	query=request.GET.get('q')
	response_data = {}
	response_data['code'] = 1
	response_data['details'] = {}
	response_data['details']['Message'] = 'Learning AJAX'


	qset = Q()
	for word in query.split('+'):
		qset |= Q(name__istartswith=query) | Q(name__icontains=' '+query)
	result = University.objects.filter(qset)[:3]

	#result = University.objects.filter(name__icontains=query)[:3]
	
	response_data['data'] = []
	for uni in result:
		response_data['data'].append(uni.name)
	    
	return HttpResponse(json.dumps(response_data), mimetype="application/json")
