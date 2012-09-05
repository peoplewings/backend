# Create your views here.
from django.contrib.auth.decorators import login_required
from wings.models import Wing
from people.models import City, PW_STATE_CHOICES
from people.forms import StatusForm
from wings.forms import WingForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

STATUS_CHOICES = []

for i in PW_STATE_CHOICES: STATUS_CHOICES.append(i[1])

@login_required
def list_wings(request):
	wings = Wing.objects.filter(host=request.user.get_profile())
  	up = request.user.get_profile()
	current_state=up.pw_state
	data = {'pw_state':current_state}
	form = StatusForm(initial=data)
	return render_to_response('wings/my_wings.html', {'wings': wings, 'form': form}, context_instance=RequestContext(request))

@login_required
def manage_wing_information(request):
    if request.method == 'POST':
        #POST = request.POST.copy()
        #POST['status'] = w.status
        form = WingForm(True, request.POST or None)
        if form.is_valid():
            pets = request.POST.getlist( 'pets' )
            transp = request.POST.getlist( 'transp' )
            print form.cleaned_data['pref_gender']
            save_wing_info(form.cleaned_data, request.user.get_profile(), request.GET.get('id', ''), pets, transp)
            return HttpResponseRedirect('/wings/list/')
    else:
        bloquear = request.user.get_profile().pw_state != 'W'
    	wing_id=request.GET.get('id', '')
    	if wing_id == '': 
            if bloquear: 
                initial={'stat':request.user.get_profile().pw_state}
                form = WingForm(bloquear, initial=initial)
            else: form = WingForm(bloquear)
            
    	else:
    		w = Wing.objects.get(pk=int(wing_id))
    		data=load_wing_info(w)
    		#form = WingForm(instance=w)
    		form = WingForm(bloquear, initial=data)
    		
    		#if request.user.get_profile().pw_state != 'W':
    			#form.fields['status'].widget.attrs['disabled'] = True
    return render_to_response('wings/wing_accomodation.html', {'form': form}, context_instance=RequestContext(request))

def load_wing_info(w):
    #initial = w.preferred_gender
    #if initial == 'B': initial = ['M','F']
    verbose_city = w.city.name + ", " + w.city.country
    pets =[]
    if w.i_have_pet: pets.append('0')
    if w.pets_allowed: pets.append('1')

    transp = []
    if w.underground: transp.append('0')
    if w.bus: transp.append('1')
    if w.tram: transp.append('2')
    if w.train: transp.append('3')
    if w.others: transp.append('4')

    pref_gender = []
    if w.preferred_gender == 'B': pref_gender = ['M', 'F']
    elif w.preferred_gender == 'M' or w.preferred_gender=='F': pref_gender.append(w.preferred_gender)

    data={'wing_name' : w.name,
		'stat' : w.status,
		'sharing_once' : w.sharing_once,
		'pref_gender' : pref_gender,
		'from_date' : w.from_date,
		'to_date' : w.to_date,
		'better_days' : w.better_days,
		'capacity' : w.capacity,
		'wheelchair' : w.wheelchair,
		'where_sleeping_type' : w.where_sleeping_type,
		'smoking' : w.smoking,

		'pets': pets,
		#'i_have_pet' : w.i_have_pet,
		#'pets_allowed' : w.pets_allowed,

		'blankets' : w.blankets,
		'live_center' : w.live_center,

        'transp' : transp,
		#'underground' : w.underground,
		#'bus' : w.bus,
		#'tram' : w.tram,
		#'train' : w.train,
		#'others' : w.others,
		'about' : w.about,
		'address' : w.address,
		'number' : w.number,
		'additional_information' : w.additional_information,
		'city' : verbose_city,
		'city_name' : w.city.name,
		'city_country' : w.city.country,
		'city_place_id' : w.city.cid,
		'postal_code' : w.postal_code
    }
    return data

def save_wing_info(data, profile, wing_id, pets, transp):
    g = data['pref_gender']
    if len(g) == 0: res = 'N'
    elif len(g) == 1: res = data['pref_gender'][0]
    else: res = 'B'

    if data['wing_name'].replace(' ', '') == '': wing_name = 'Accommodation ' + data['city_name']
    else: wing_name = data['city_name']

    if wing_id == '': w = Wing.objects.create(host=profile, name=wing_name)
    else: w = Wing.objects.get(pk=int(wing_id))

    if data['stat']: w.status = data['stat']
    else: w.status = profile.pw_state

    w.sharing_once = data['sharing_once']
    w.preferred_gender=res
    w.from_date = data['from_date']
    w.to_date = data['to_date']
    w.better_days = data['better_days']
    w.capacity = data['capacity']
    w.wheelchair = data['wheelchair']
    w.where_sleeping_type = data['where_sleeping_type']
    w.smoking = data['smoking']

    w.i_have_pet = '0' in pets
    w.pets_allowed = '1' in pets
    #w.i_have_pet = data['i_have_pet']
    #w.pets_allowed = data['pets_allowed']

    w.blankets = data['blankets']
    w.live_center = data['live_center']

    w.underground = '0' in transp
    w.bus = '1' in transp
    w.tram = '2' in transp
    w.train = '3' in transp
    w.others = '4' in transp
    #w.underground = data['underground']
    #w.bus = data['bus']
    #w.tram = data['tram']
    #w.train = data['train']
    #w.others = data['others']
    w.about = data['about']
    w.address = data['address']
    w.number = data['number']
    w.additional_information = data['additional_information']
    w.city, b = City.objects.get_or_create(cid=data['city_place_id'], name=data['city_name'], country=data['city_country'])
    #w.city, b = City.objects.get_or_create(name=city_name, country=country)
    w.postal_code = data['postal_code']
    w.save()

@login_required
def delete_wing(request, wing_id):
	try:
		w = Wing.objects.get(pk=int(wing_id))
		w.delete()
	except: pass
	return HttpResponseRedirect('/wings/list/')

