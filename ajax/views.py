# Create your views here.
from people.models import University
import json
import datetime
from peoplewings.settings import MEDIA_ROOT
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def search_university(request):
	query=request.GET.get('q')
	response_data = {}
	#response_data['code'] = 1
	response_data['details'] = {}
	response_data['details']['Message'] = 'Learning AJAX'
	
	qset = Q()
	qset = Q(name__istartswith=query) | Q(name__icontains=' '+query)
	
	try:
		result = University.objects.filter(qset)[:5]

		#result = University.objects.filter(name__icontains=query)[:3]
	
		response_data['data'] = []
		for uni in result:
			response_data['data'].append(uni.name)

	except Exception as e:
		response_data['details']['Message'] = e.message

	response_data['code'] = HttpResponse.status_code
	    
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

@login_required
def upload_image(request):
    response = {'success':False}
    if request.method == 'POST':
        #, path=str(request.user.pk) + "/"
        if save_file(request.FILES['fileToUpload']):  response = {'success':True}
    js = json.dumps(response)
    return HttpResponse(js, mimetype='application/json')

def save_file(file, path=''):
    ''' Little helper to save a file
    '''
    #filename = file._get_name()
    filename = "avatar.jpg"
    fd = open('%s/%s' % (MEDIA_ROOT, str(path) + str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()
    return True

