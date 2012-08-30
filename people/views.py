# Create your views here.
from people.models import UserProfile, UserLanguage, UserProfileStudiedUniversity, UserSocialNetwork, UserInstantMessage, City
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.core.urlresolvers import reverse
import smtplib, random, string, md5, os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from people import signals
from django.template import RequestContext
from people.forms import *
from django.forms.formsets import formset_factory
from datetime import date
import re
from django.utils import simplejson
from wings.models import Wing

@login_required
def view_profile(request):
  """
    Outputs the following data from the profile passed as parameter: gender, date of birth
    interested in, civil state, languages, city, pw state, all about you, main mission
    occupation, education, pw experience, personal philosophy, other pages you like, 
    people you like, favourite books, movies, series, etc, what you like teaching or sharing,
    incredible things you have done or seen, opinion about peoplewings, political opinion, religion, 
    quotes, people that inspired you.
  """
  #request.session.set_expiry(5)
  user = request.user
  up = user.get_profile()
  form = CustomProfileForm(instance = up)
  if request.user.is_authenticated(): return render_to_response('people/profile.html', {'profile': up, 'user': up.user})
  return render_to_response('people/login.html')
    
"""
BasicInfoFormSet = formset_factory(BasicInformationForm, extra=1)
formset = BasicInfoFormSet()
return render_to_response('people/basic_info.html',  {'formset': formset}, context_instance=RequestContext(request))
"""
@login_required
def manage_basic_information(request):
    BasicInfoFormSet = formset_factory(BasicInformationForm, extra=0)
    LangFormSet = formset_factory(LanguageForm, formset=LanguageFormSet, extra=0)
    if request.method == 'POST':
        formset = BasicInfoFormSet(request.POST, request.FILES)
        langset = LangFormSet(request.POST,  prefix='lang')
        if formset.is_valid() and langset.is_valid():
            save_basic_info(formset.cleaned_data, langset.cleaned_data, request.user)
            return HttpResponseRedirect('/users/profile/')
    else:
        initial = load_basic_data(request.user)
        formset = BasicInfoFormSet(initial=initial)
        uid = request.user.get_profile().id
        data = []
        for lang in UserLanguage.objects.filter(user_profile_id=uid):
            data.append({'language': lang.language_id, 'level': lang.level})
        if (len(data) == 0): LangFormSet = formset_factory(LanguageForm, formset=LanguageFormSet, extra=1)
        langset = LangFormSet(initial=data, prefix='lang')
    return render_to_response('people/basic_info.html', {'formset': formset, 'langset': langset, 'profile_id': uid}, context_instance=RequestContext(request))


def load_basic_data(user):
    up = user.get_profile()
    initial = up.interested_in
    if initial == 'B': initial = ['M','F']
    data = [{ 'gender': up.gender, 
            'show_birthday': up.show_birthday, 
            'birthday' :up.birthday,
            'interested_in': initial,
            'civil_state': up.civil_state
    }]
    return data

def save_basic_info(info, langs, user):
    data=info[0]
    profile = user.get_profile()
    interested_len = len(data['interested_in'])
    if interested_len > 0 :
        if interested_len == 1 : 
            profile.interested_in = data['interested_in'][0] 
        else: profile.interested_in = 'B'
    else:
        profile.interested_in = 'N'
    profile.gender = data['gender']
    profile.show_birthday = data['show_birthday']
    profile.civil_state = data['civil_state']
    profile.birthday = data['birthday']
    today = date.today()
    age = today.year - profile.birthday.year
    if today.month < profile.birthday.month or (today.month == profile.birthday.month and today.day < profile.birthday.day): age -= 1
    profile.age = age
    UserLanguage.objects.filter(user_profile_id=profile.id).delete()
    for lang in langs:
        if len(lang) > 1:
            user_lan = UserLanguage.objects.get_or_create(user_profile_id=profile.id, language_id=lang['language'], level=lang['level'])
    profile.save()




# CONTACT INFORMATION VIEW (LOAD/SAVE)
@login_required
def manage_contact_information(request):
    ContactInfoFormSet = formset_factory(ContactInformationForm, extra=0)
    SNFormSet = formset_factory(SocialNetworkForm, formset=SocialNetworkFormSet, extra=0)
    IMFormSet = formset_factory(InstantMessageForm, formset=InstantMessageFormSet, extra=0)
    if request.method == 'POST':
        print request.POST
        formset = ContactInfoFormSet(request.POST, request.FILES)
        snset = SNFormSet(request.POST,  prefix='sn')
        imset = IMFormSet(request.POST, prefix='im')
        if formset.is_valid() and snset.is_valid() and imset.is_valid():
            save_contact_info(formset.cleaned_data, snset.cleaned_data, imset.cleaned_data, request.user)
            return HttpResponseRedirect('/users/profile/')
    else:
        initial = load_contact_data(request.user)
        formset = ContactInfoFormSet(initial=initial)
        uid = request.user.get_profile().id
        sns = []
        ims = []
        for sn in UserSocialNetwork.objects.filter(user_profile_id=uid):
            sns.append({'social_network': sn.social_network.id, 'social_network_username': sn.social_network_username})
        for im in UserInstantMessage.objects.filter(user_profile_id=uid):
            ims.append({'instant_message': im.instant_message.id, 'instant_message_username': im.instant_message_username})
        if len(sns) == 0: SNFormSet = formset_factory(SocialNetworkForm,  extra=1)
        if len(ims) == 0: IMFormSet = formset_factory(InstantMessageForm, formset=InstantMessageFormSet, extra=1)
        snset = SNFormSet(initial=sns, prefix='sn')
        imset = IMFormSet(initial=ims, prefix='im')
    return render_to_response('people/contact_info.html', {'formset1': formset, 'formset2': snset, 'formset3': imset}, context_instance=RequestContext(request))

def load_contact_data(user):
    up = user.get_profile()
    data = [{ 'phone': up.phone, 
            'emails': up.emails
    }]
    return data

def save_contact_info(info, snset, imset, user):
    data=info[0]
    profile = user.get_profile()
    profile.phone = data['phone']
    profile.emails = data['emails']
    # borramos todas las asociaciones que tenia este profile con sus redes sociales y sus mensajes instantaneos...
    UserSocialNetwork.objects.filter(user_profile_id=profile.id).delete()
    UserInstantMessage.objects.filter(user_profile_id=profile.id).delete()
    # ... e insertamos las nuevas pasadas por POST
    for sn in snset:
      UserSocialNetwork.objects.create(user_profile_id=profile.id, social_network_id=sn['social_network'], social_network_username=sn['social_network_username'])
    for im in imset:
      UserInstantMessage.objects.create(user_profile_id=profile.id, instant_message_id=im['instant_message'], instant_message_username=im['instant_message_username'])
    profile.save()


@login_required
def manage_likes_information(request):
    if request.method == 'POST':
        form = LikesForm(request.POST or None)
        if form.is_valid():
            form.save()
            #save_likes_info(form.cleaned_data, request.user)
            return HttpResponseRedirect('/users/profile/')
    else:
        form = LikesForm(instance=request.user.get_profile())
    return render_to_response('people/likes_info.html', {'form': form}, context_instance=RequestContext(request))

    
def save_likes_info(data, user):
    #print data
    profile = user.get_profile()
    profile.movies=data['movies']
    profile.inspired_by=data['inspired_by']
    profile.other_pages=data['other_pages']
    profile.quotes=data['quotes']
    profile.sharing=data['sharing']
    profile.sports=data['sports']
    profile.enjoy_people=data['enjoy_people']
    profile.incredible=data['incredible']
    profile.pw_opinion=data['pw_opinion']
    profile.save()

@login_required
def manage_locations_information(request):
    CitiesFormset = formset_factory(UserLocationForm, extra=0)
    LocationFormset = formset_factory(AnotherLocationForm, extra=0)
    if request.method == 'POST':
        formset = CitiesFormset(request.POST or None)
        if formset.is_valid():
            #print formset1.cleaned_data
            save_locations_info(formset.cleaned_data, request.user)
            return HttpResponseRedirect('/users/yoho/')
        else: print formset1.errors
    else:
        initial = load_location_data(request.user)
        if (len(initial) > 0):
            #CitiesFormset = formset_factory(UserLocationForm, extra=0)
            formset = CitiesFormset(initial=initial)
            LocationFormset = formset_factory(AnotherLocationForm, extra=1)
            locationset = LocationFormset()
        else:
            CitiesFormset = formset_factory(UserLocationForm, extra=1)
            locationset = LocationFormset()
            formset = CitiesFormset()
    #'formset2': locationset
    return render_to_response('people/location_info.html', {'formset1': formset}, context_instance=RequestContext(request))

def save_locations_info(data, user):
    profile = user.get_profile()
    data=data[0]
    hometown = City.objects.get_or_create(cid=data['home_place_id'], name=data['home_city'], country=data['home_country'])
    current = City.objects.get_or_create(cid=data['current_city_place_id'], name=data['current_city_city'], country=data['current_city_country'])
    profile.hometown = hometown[0]
    profile.current_city = current[0]
    profile.save()

def load_location_data(user):
    profile = user.get_profile()
    verbose_home = profile.hometown.name + ", " + profile.hometown.country
    verbose_current = profile.current_city.name + ", " + profile.current_city.country 
    data = [{
            'hometown': verbose_home,
            'home_city': profile.hometown.name, 
            'home_country': profile.hometown.country, 
            'home_place_id': profile.hometown.cid,  
            'current_city': verbose_current,
            'current_city_city': profile.current_city.name, 
            'current_city_country': profile.current_city.country,
            'current_city_place_id': profile.current_city.cid 
    }]
    return data

    

# ABOUT ME VIEW (LOAD/SAVE)
@login_required
def manage_about_information(request):
    AboutMeFormSet1 = formset_factory(AboutMeForm1, extra=0)
    EduFormSet = formset_factory(EducationForm, formset=EducationFormSet, extra=0)
    AboutMeFormSet2 = formset_factory(AboutMeForm2, extra=0)
    if request.method == 'POST':
        formset1 = AboutMeFormSet1(request.POST, request.FILES)
        formset2 = AboutMeFormSet2(request.POST, request.FILES, prefix='f2')
        eduset = EduFormSet(request.POST,  prefix='edu')
        if formset1.is_valid() and eduset.is_valid() and formset2.is_valid():
            save_about_info(formset1.cleaned_data, eduset.cleaned_data, formset2.cleaned_data, request.user)
            return HttpResponseRedirect('/users/profile/')
    else:
        initial1 = load_about_data1(request.user)
        initial2 = load_about_data2(request.user)
        formset1 = AboutMeFormSet1(initial=initial1)
        formset2 = AboutMeFormSet2(initial=initial2, prefix='f2')
        uid = request.user.get_profile().id
        edus = []
        for edu in UserProfileStudiedUniversity.objects.filter(user_profile_id=uid):
            edus.append({'institution': edu.university.name, 'degree': edu.degree})
        if len(edus) == 0: EduFormSet = formset_factory(EducationForm, formset=EducationFormSet, extra=1)
        eduset = EduFormSet(initial=edus, prefix='edu')
    return render_to_response('people/about_info.html', {'formset1': formset1, 'formset2': eduset, 'formset3': formset2}, context_instance=RequestContext(request))

def load_about_data1(user):
    up = user.get_profile()
    data = [{ 'all_about_you': up.all_about_you, 
            'main_mission': up.main_mission,
            'occupation': up.occupation,
            'company': up.company
    }]
    return data

def load_about_data2(user):
    up = user.get_profile()
    data = [{
            'personal_philosophy': up.personal_philosophy,
            'political_opinion': up.political_opinion,
            'religion': up.religion
    }]
    return data
"""
info y info2: dos formsets que contienen solo 1 form AboutMeForm1 y AboutMeForm2
eduset: formset que contiene n forms EducationForm, cada uno con institution y degree
"""
def save_about_info(info, eduset, info2, user):
    data=info[0] # un form AboutMeForm1
    data2=info2[0] # un form AboutMeForm2
    profile = user.get_profile()
    profile.all_about_you = data['all_about_you']
    profile.main_mission = data['main_mission']
    profile.occupation = data['occupation']
    profile.company = data['company']
    profile.personal_philosophy = data2['personal_philosophy']
    profile.political_opinion = data2['political_opinion']
    profile.religion = data2['religion']
    UserProfileStudiedUniversity.objects.filter(user_profile_id=profile.id).delete()
    for edu in eduset:
        if len(edu) > 1:
            u = University.objects.get_or_create(name=edu['institution'])
            UserProfileStudiedUniversity.objects.create(user_profile_id=profile.id, university_id=u[0].id, degree=edu['degree'])
    profile.save()

@login_required
def view_account_settings(request):
  user = request.user
  if request.user.is_authenticated(): return render_to_response('people/account.html', {'user': user})
  return render_to_response('people/login.html')

@login_required
def enter_edit_account_settings(request):
  user = request.user
  form = CustomAccountSettingsForm(instance=user)
  if request.user.is_authenticated(): return render_to_response('people/editableAccount.html', {'form': form}, context_instance = RequestContext(request))
  return render_to_response('people/login.html')

@login_required
def edit_account_settings(request):
  p1 = request.POST['password']
  p2 = request.POST['repassword']
  user = request.user
  if request.user.is_authenticated():
  	if p1 == p2:
  		user.set_password(p1)
  		user.save()
  	return HttpResponseRedirect('/users/account/')
  return render_to_response('people/login.html')

def search(request):
  #age_from = request.POST['age_from']
  #age_up_to = request.POST['age_up_to']
  # quitar esto
  age_from=34
  age_up_to=34
  # gte = greater o equal than, gt = greater than
  results = UserProfile.objects.all().filter(age__gte=age_from).exclude(age__gt=age_up_to)
  return render_to_response('people/login.html', {'results':results})

@login_required
def delete(request):
  signals.user_deleted.send(sender=User, request=request)
  user = request.user
  user.delete()
  return HttpResponseRedirect('/login/')

@login_required
def update_status(request):
  if request.method == 'POST':
        form = StatusForm(request.POST or None)
        if form.is_valid():
          up = request.user.get_profile()
          up.pw_state = form.cleaned_data['pw_state']
          up.save()
          if up.pw_state != 'W': wings = Wing.objects.filter(author=up).update(status=up.pw_state)
          return HttpResponseRedirect('/wings/list/')


@login_required
def enter_edit_account_settings(request):
  user = request.user
  form = CustomAccountSettingsForm(instance=user)
  if request.user.is_authenticated(): return render_to_response('people/editableAccount.html', {'form': form}, context_instance = RequestContext(request))
  return render_to_response('people/login.html')
