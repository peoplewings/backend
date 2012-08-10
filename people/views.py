# Create your views here.
from people.models import UserProfile, University, Language, UserLanguage
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.core.urlresolvers import reverse
import smtplib, random, string, md5, os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from people import signals
from django.template import RequestContext
from people.forms import *
from django.forms.formsets import formset_factory
from datetime import date
import re

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
  user = request.user
  up = user.get_profile()
  form = CustomProfileForm(instance = up)
  if request.user.is_authenticated(): return render_to_response('people/profile.html', {'profile': up, 'user': up.user})
  return render_to_response('people/login.html')

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
    if request.user.is_authenticated(): return render_to_response('people/basic_info.html', {'formset': formset, 'langset': langset}, context_instance=RequestContext(request))
    return render_to_response('people/login.html')

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
    for lang in langs:
        user_lan = UserLanguage.objects.get_or_create(user_profile_id=profile.id, language_id=lang['language'], level=lang['level'])
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
def enter_edit_account_settings(request):
  user = request.user
  form = CustomAccountSettingsForm(instance=user)
  if request.user.is_authenticated(): return render_to_response('people/editableAccount.html', {'form': form}, context_instance = RequestContext(request))
  return render_to_response('people/login.html')