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
from datetime import date
import re

@login_required
def viewProfile(request):
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
def enterEditProfile(request):
  user = request.user
  up = user.get_profile()
  form = CustomProfileForm(instance = up)
  if request.user.is_authenticated(): return render_to_response('people/editableProfile.html', {'form': form, 'nextAction':"/users/profile/edit/completed/"}, context_instance = RequestContext(request))
  return render_to_response('people/login.html')

@login_required
def enterEditBasicInformation(request):
  user = request.user
  up = user.get_profile()
  initial = up.interested_in
  if initial == 'B': initial = ['M','F'] 
  form = BasicInformationForm(instance = up, initial={'interested_in': initial})
  if request.user.is_authenticated(): return render_to_response('people/editableProfile.html', {'form': form, 'nextAction':"/users/basic/edit/completed/"}, context_instance = RequestContext(request))
  return render_to_response('people/login.html')

@login_required
def editProfile(request):
  
  user = request.user
  up = user.get_profile()
  form = CustomProfileForm(request.POST, instance=up)

  if request.user.is_authenticated():
    if form.is_valid():
      form.save()

      today = date.today()
      b = up.birthday
      age = today.year - b.year
      if today.month < b.month or (today.month == b.month and today.day < b.day): age -= 1
      up.age = age
      """
      universities = request.POST['uni'].split(',')
      for uni in universities:
        if len(uni.replace(" ", "")) != 0:
          if University.objects.filter(name=uni): # si ya existe la uni en la base de datos...
            u = University.objects.get(name=uni)
          else:                                   # el usuario ha insertado una uni nueva => la insertamos en la BD
            u = University.objects.create(name=uni)
          up.universities.add(u)
      """
      up.save()
    else: print "form is NOT valid"
    return HttpResponseRedirect('/users/profile/')
  return render_to_response('registration/login.html')

@login_required
def editBasicInformation(request):
    form = BasicInformationForm(request.POST or None)
    print request.POST
    if form.is_valid():
	  save_basic_info(form.cleaned_data, request.user)
	  return HttpResponseRedirect('/users/profile/')
    print "ERROR: form not valid"
    return render_to_response('registration/login.html')

def save_basic_info(data, user):
    print data
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
    user_lan = UserLanguage(user_profile_id=profile.id, language_id=data['lang'], level=data['level'])
    user_lan.save()
    profile.save()

@login_required
def viewAccountSettings(request):
  user = request.user
  if request.user.is_authenticated(): return render_to_response('people/account.html', {'user': user})
  return render_to_response('people/login.html')

@login_required
def enterEditAccountSettings(request):
  user = request.user
  form = CustomAccountSettingsForm(instance=user)
  if request.user.is_authenticated(): return render_to_response('people/editableAccount.html', {'form': form}, context_instance = RequestContext(request))
  return render_to_response('people/login.html')

@login_required
def editAccountSettings(request):
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


