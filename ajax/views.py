# Create your views here.
from django.views.decorators.csrf import csrf_protect
from people.models import University, Photo
from people.forms import ImageForm, CropForm
import json
from datetime import datetime
import os
import errno
import random
import Image
from imagekit.models.fields import ProcessedImageField
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
        request.POST['owner'] = request.user.get_profile().id
        print request.POST, request.FILES
        form = ImageForm(request.POST, request.FILES)
        #b, f, e = save_user_image(request.FILES['processed_image'], request.POST['uid'], request.POST['is_avatar'])
        if form.is_valid():     
             photo = form.save()
             response = {'success': True, 'filename': request.FILES['processed_image']._name, 'fid': photo.pk}
    js = json.dumps(response)
    return HttpResponse(js, mimetype='application/json')

@csrf_protect
def crop_avatar(request):
    response = {'success':False}
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES)
        if form.is_valid():
             crop_image(request.user.get_profile().id, form.cleaned_data['fid'], form.cleaned_data['x1'], form.cleaned_data['y1'], form.cleaned_data['x2'], form.cleaned_data['y2'], form.cleaned_data['w'], form.cleaned_data['h'])
             #Photo.objects.get(owner=request.POST['owner'], )
             #form.save()
             #response = {'success': True, 'filename': request.FILES['processed_image']._name}
        else: print form.errors
    js = json.dumps(response)
    return HttpResponse(js, mimetype='application/json')


def crop_image(uid, image_id, x1, y1, x2, y2, w, h):
    original = Photo.objects.get(pk=image_id)
    im = Image.open(original.processed_image)
    boxcrop = (int(x1),int(y1),int(x2),int(y2))
    kay = im.crop(box=boxcrop)
    #print im.size, im.info
    #print kay.load()
    #filename = original.processed_image.name.split('/')[-1]
    filename = "avatar.gif"
    path = os.path.join(MEDIA_ROOT, str(uid), filename)
    kay.save(path)
    data = {
        'owner': uid,
        'processed_image': kay
    }
    form = ImageForm(data)
    form.save()
    #cropped = Photo.objects.create(owner_id=uid, processed_image=crop)
    #original.delete()
"""
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



def check_file_exists(path, filename):
    try:
        f = os.path.normpath(os.path.join(path, filename))
        print f
        with open(f) as f: pass
    except IOError as e:
        raise
"""