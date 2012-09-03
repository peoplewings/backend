# Create your views here.
from people.models import UserProfile, City
from wings.models import Wing
from search.forms import SearchForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

def manage_search(request):

    if request.method == 'POST':
        form = SearchForm(request.POST or None)
        if form.is_valid():
            results = get_results(form.cleaned_data, request)
            return render_to_response('search/list_results.html', {'results':results})
    else:
        form = SearchForm()
    return render_to_response('search/search.html', {'form': form}, context_instance=RequestContext(request))

def get_results(data, request):
    #print data

    #WING CRITERIA
    if data['city_name'] != '':
        city_name = data['city_name']
        # documentation in https://docs.djangoproject.com/en/dev/topics/db/queries/#spanning-multi-valued-relationships
    elif request.user.get_profile().current_city != None:
        city_name = request.user.get_profile().current_city.name.encode('utf-8')
    else: city_name=''
    #print request.user.get_profile().current_city.name.encode('utf-8')
    wings = Wing.objects.filter(city__name__icontains=city_name, capacity__gte=data['capacity'])
    if data['start_date'] != None: wings = wings.exclude(to_date__isnull=False, to_date__lt=data['start_date'])
    if data['end_date'] != None: wings = wings.exclude(from_date__isnull=False, from_date__gt=data['end_date'])
    # al final de las alas que cumplen nuestros criterios de busqueda, hay que quitar aquellas 
    # en las que se prefiera a gente de sexo diferente al nuestro:
    wings = wings.filter(Q(preferred_gender='B') | Q(preferred_gender=request.user.get_profile().gender))

    # PEOPLE CRITERIA
    wings_ids= []
    for w in wings: 
        wings_ids.append(w.id)
        print w.name
    #print wings_ids
    results = UserProfile.objects.filter(wing__id__in=wings_ids)
    if data['start_age'] != None: results = results.exclude(age__lt=data['start_age'])
    if data['end_age'] != None: results = results.exclude(age__gt=data['end_age'])
    if data['language'] != '': results = results.filter(languages__name=data['language'])
    if data['gender']: results = results.filter(gender__in=data['gender'])
    """
            # gte = greater o equal than, gt = greater than
            results = UserProfile.objects.all().filter(age__gte=age_from).exclude(age__gt=age_up_to)
    """

    return results