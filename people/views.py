# Create your views here.
from people.models import UserProfile
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.core.urlresolvers import reverse
import smtplib, random, string, md5, os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from people import signals

def info(request):
  user = request.user
  up = user.get_profile()
  if request.user.is_authenticated(): return render_to_response('people/profile.html', {'profile': up})
  return render_to_response('people/login.html')

def viewProfile(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def enterEditProfile(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def editProfile(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def viewAccountSettings(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def enterEditAccountSettings(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def editAccountSettings(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def delete(request):
  signals.user_deleted.send(sender=User, request=request)
  user = request.user
  user.delete()
  return render_to_response('landing/home.html')

