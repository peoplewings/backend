# Create your views here.
from django.views.decorators.csrf import csrf_protect
from people.models import University
import json
from datetime import datetime
import os
import errno
import random
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

@csrf_protect
def upload_image(request):
    response = {'success':False}
    if request.method == 'POST':
        #, path=str(request.user.pk) + "/"
        b, f, e = save_user_image(request.FILES['fileToUpload'], request.POST['uid'], request.POST['is_avatar'])
        response = {'success':b, 'avatar':f, 'extension':e}
    js = json.dumps(response)
    return HttpResponse(js, mimetype='application/json')

def save_user_image(file, profile_id, avatar=False):
    ext = file._get_name().split('.')[1]
    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%s") + '.' + ext
    if avatar:
        filename = str(os.urandom(16).encode('hex'))
    if save_file(file, filename + '.' + ext, profile_id): return True, filename, ext
    return False


def save_file(file, filename, uid):
    path = os.path.normpath(os.path.join(MEDIA_ROOT, uid + '/'))
    make_sure_path_exists(path)
    fd = open('%s/%s' % (path, str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()
    return True

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


"""
def check_file_exists(path, filename):
    try:
        f = os.path.normpath(os.path.join(path, filename))
        print f
        with open(f) as f: pass
    except IOError as e:
        raise
"""