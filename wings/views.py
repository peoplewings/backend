# Create your views here.
from django.contrib.auth.decorators import login_required
from wings.models import Wing
from people.models import City
from wings.forms import WingForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def list_wings(request):
	wings = Wing.objects.filter(author=request.user.get_profile())
	return render_to_response('wings/my_wings.html', {'wings': wings}, context_instance=RequestContext(request))

@login_required
def manage_wing_information(request):
    if request.method == 'POST':
        form = WingForm(request.POST or None)
        if form.is_valid():
            #print "wing form is valid"
            save_wing_info(form.cleaned_data, request.user.get_profile(), request.GET.get('id', ''))
            #form.save()
            return HttpResponseRedirect('/users/profile/')
        #else: print "error en el wing form"
    else:
    	wing_id=request.GET.get('id', '')
    	if wing_id == '': form = WingForm()
    	else: 
    		w = Wing.objects.get(pk=int(wing_id))
    		data=load_wing_info(w)
    		#form = WingForm(instance=w)
    		form = WingForm(initial=data)
    return render_to_response('people/wings.html', {'form': form}, context_instance=RequestContext(request))

def load_wing_info(w):
	initial = w.preferred_gender
	if initial == 'B': initial = ['M','F']
	print "city name: ", w.city.name
	print "country name: ", w.city.country
	verbose_city = w.city.name + ", " + w.city.country
	data={'name' : w.name,
		'status' : w.status,
		'sharing_once' : w.sharing_once,
		'pref_gender' : initial,
		'from_date' : w.from_date,
		'to_date' : w.to_date,
		'better_days' : w.better_days,
		'capacity' : w.capacity,
		'wheelchair' : w.wheelchair,
		'where_sleeping_type' : w.where_sleeping_type,
		'smoking' : w.smoking,
		'i_have_pet' : w.i_have_pet,
		'pets_allowed' : w.pets_allowed,
		'blankets' : w.blankets,
		'live_center' : w.live_center,
		'underground' : w.underground,
		'bus' : w.bus,
		'tram' : w.tram,
		'train' : w.train,
		'others' : w.others,
		'about' : w.about,
		'address' : w.address,
		'number' : w.number,
		'additional_information' : w.additional_information,
		'hometown' : verbose_city,
		'city_name' : w.city.name,
		'country' : w.city.country,
		'place_id' : w.city.cid,
		'postal_code' : w.postal_code
	}
	return data

def save_wing_info(data, profile, wing_id):

	g = data['pref_gender']
	if len(g) == 0: res = 'N'
	elif len(g) == 1: res = data['pref_gender'][0]
	else: res = 'B'

	if wing_id == '': w = Wing.objects.create(author=profile)
	else: w = Wing.objects.get(pk=int(wing_id))

	w.name = data['name']
	w.status = data['status']
	w.sharing_once = data['sharing_once']
	w.preferred_gender=res
	w.from_date = data['from_date']
	w.to_date = data['to_date']
	w.better_days = data['better_days']
	w.capacity = data['capacity']
	w.wheelchair = data['wheelchair']
	w.where_sleeping_type = data['where_sleeping_type']
	w.smoking = data['smoking']
	w.i_have_pet = data['i_have_pet']
	w.pets_allowed = data['pets_allowed']
	w.blankets = data['blankets']
	w.live_center = data['live_center']
	w.underground = data['underground']
	w.bus = data['bus']
	w.tram = data['tram']
	w.train = data['train']
	w.others = data['others']
	w.about = data['about']
	w.address = data['address']
	w.number = data['number']
	w.additional_information = data['additional_information']

	a=data['hometown'].split(',')
	#print a
	if len(a) == 2:
		city_name=a[0]
		country=a[1]
		#print "city name: ", city_name
		#print "country: ", country 
		print "data", data
		w.city, b = City.objects.get_or_create(cid=data['place_id'], name=data['city_name'], country=data['country'])
		#w.city, b = City.objects.get_or_create(name=city_name, country=country)
	w.postal_code = data['postal_code']
	w.save()

@login_required
def delete_wing(request, wing_id):
	try:
		w = Wing.objects.get(pk=int(wing_id))
		w.delete()
	except: pass
	return HttpResponseRedirect('/users/profile/')

