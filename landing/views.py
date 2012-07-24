from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
import smtplib, random, string, md5, os, datetime
from django.contrib.auth.models import User

def welcome(request):
    name = 'pepe'
    now = datetime.datetime.now()
    return render_to_response('home.html', {'name': name, 'time': now})