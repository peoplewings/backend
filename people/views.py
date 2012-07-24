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

def viewProfile(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def enterEditProfile(request, people_id):
  user = get_object_or_404(people, id=people_id)
  return render_to_response('people/profile.html', {'user': user})

def login(request, **kwargs):
        email, password = kwargs['email'], kwargs['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        # username = kwargs['first_name'] + "." + kwargs['last_name'] 
        new_user = get_object_or_404(RegistrationProfile, email=email)
        user = authenticate(username=new_user.username, password=password)
        if user is not None:
            login(request, user)
            request.session['user'] = user
                                                    
        return user