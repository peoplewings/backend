# Create your views here.
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from pprint import pprint
import os
from django.utils import simplejson
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource

from peoplewings.apps.cropper.models import Original
from peoplewings.apps.people.models import University, Relationship, UserProfile
from peoplewings.apps.notifications.models import Notifications
from peoplewings.apps.wings.models import Wing
from peoplewings.apps.registration.views import api_token_is_authenticated


def search_university(request):
    query=request.GET.get('q')
    response_data = {}
    response_data['msg'] = 'Universities retrieved successfully.'
    response_data['status'] = True

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

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

@csrf_protect
def search_notification_addressees(request):
    notif_type=request.GET.get('type')
    apitoken = api_token_is_authenticated(request)
    if not apitoken: return ModelResource().create_response(request, {"code" : 401, "status" : False, "msg": "Unauthorized"}, response_class=HttpForbidden)
    
    if notif_type not in ('request', 'invitation', 'message'):
        response_data = {}
        response_data['error'] = 'Type not valid.'
        response_data['status'] = False
        response_data['code'] = 400
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    # parte comun: 
    # 1. obtener los usuarios que nos enviaron Messages, Invitations o Requests
    up = UserProfile.objects.get(user=apitoken)
    notifs = Notifications.objects.filter(Q(sender=up) | Q(receiver=up))
    result = set()
    for i in notifs:
        if i.sender == up: result.add(i.receiver) 
        else: result.add(i.sender)
    # 2. union con My Friends
    rels = Relationship.objects.filter(Q(sender=up) | Q(receiver=up), relationship_type='Accepted')
    result2 = set()
    for i in rels:
        if i.sender == up: result2.add(i.receiver) 
        else: result2.add(i.sender)
    result = result.union(result2)

    # parte especifica: si type es 'request', filtrar el listado anterior por aquellos que tengan alas.
    result = list(result)
    if notif_type == 'request':
        for i in result:
            if not Wings.objects.filter(author=i).exists(): result.remove(i)

    r = []
    for i in result:
        dic = {}
        dic['first_name'] = i.user.first_name
        dic['last_name'] = i.user.last_name
        dic['id'] = i.id
        r.append(dic)

    response_data = {}
    response_data['msg'] = 'Candidates retrieved successfully.'
    response_data['status'] = True
    response_data['code'] = 200
    response_data['data'] = r

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

@csrf_protect
def delete_image(request, original_id):
    response = {'success':False}
    if request.method == 'POST':
        original = Original.objects.get(pk=int(original_id))
        os.remove(os.path.join(settings.MEDIA_ROOT, original.image.name))
        original.delete()
    # Poner respuesta bonita
    #response = {'success': True, 'filename': request.FILES['processed_image']._name, 'fid': photo.pk}
    js = simplejson.dumps(response)
    return HttpResponse(js, mimetype='application/json')


"""
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