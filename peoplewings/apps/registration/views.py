"""
Views which allow users to create and activate accounts.

"""
import random
import datetime
from django.utils.timezone import utc
import time

from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login as auth_login, authenticate
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.registration.backends import get_backend
from peoplewings.apps.registration.exceptions import NotActive, AuthFail, BadParameters, NotAKey
from django.contrib.auth.models import User
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.registration.models import *
from django.conf import settings


def activate(request, backend, template_name='registration/activate.html', success_url=None, extra_context=None, **kwargs):
	backend = get_backend(backend)
	account = backend.activate(request, **kwargs)
	if account:
	## All OK
		return account
	## Not OK
	return


def register(request, POST, backend, success_url=None, form_class=None,
			 disallowed_url='registration_disallowed',
			 template_name='registration/registration_form.html',
			 extra_context=None):

	POST['username'] = POST['email']
	POST['password2'] = POST['password']
	if POST['email'] != POST['repeatEmail']: 
		bundle = {"email": ["Emails don't match"]}    
		raise BadParameters(bundle)
	bundle_data = POST
	backend = get_backend(backend)
	if not backend.registration_allowed(request):
		return redirect(disallowed_url)
	
	new_user = backend.register(request, **bundle_data)
	return new_user.email

def do_login(request, username, password):
	try:
		user = authenticate(username=username, password=password)
	except:
		user = None
	if user:
		if user.is_active:
			# Update last login
			user.last_login = datetime.datetime.utcnow().replace(tzinfo=utc)
			user.save() 
			return user
		else:
			raise NotActive()
	else:
		raise AuthFail()

def login(bundle):
	## Checks if the user/pass is valid    
	user = do_login(request=bundle, username = bundle.data['username'], password = bundle.data['password'])
	## Creates a new ApiToken to simulate a session. The ApiToken is totally empty
	if 'remember' in bundle.data and bundle.data['remember'] == 'on':
		api_token = ApiToken.objects.create(user=user, last = datetime.datetime.now(), last_js = int(datetime.datetime.now().strftime('%s')), remember=True)
	else:
		api_token = ApiToken.objects.create(user=user, last = datetime.datetime.now(), last_js =int(datetime.datetime.now().strftime('%s')))
	## Links the user to the token
	api_token.save()
	try:
		pf = UserProfile.objects.get(user=user)
		ret = dict(token=api_token.token, idUser=user.pk)
		if pf.tutorial:
			ret["tutorial"] = False
		else:
			ret["tutorial"] = True
	except:
	   raise AuthFail() 
	
	return ret

def api_token_is_authenticated(bundle, **kwargs):
	#import pdb; pdb.set_trace()
	##Check if the user exists
	token = bundle.META.get("HTTP_X_AUTH_TOKEN")
	#import pdb; pdb.set_trace()
	try: 
		apitoken = ApiToken.objects.get(token = token)
		if apitoken.remember and apitoken.last_js + 7776000 < long(datetime.datetime.now().strftime('%s')):
			return False
		elif not apitoken.remember and apitoken.last_js + 900 < long(datetime.datetime.now().strftime('%s')):
			return False

		apitoken.last = datetime.datetime.now()
		apitoken.last_js = int(datetime.datetime.now().strftime('%s'))
		apitoken.save()
		user = User.objects.get(pk=apitoken.user_id)
		return user        
	except:
		return False

def blitline_token_is_authenticated(apitoken):
	#import pdb; pdb.set_trace()
	##Check if the user exists
	try: 
		if apitoken.remember and apitoken.last_js + 7776000 < long(datetime.datetime.now().strftime('%s')):
			return False
		elif not apitoken.remember and apitoken.last_js + 900 < long(datetime.datetime.now().strftime('%s')):
			return False

		apitoken.last = datetime.datetime.now()
		apitoken.last_js = int(datetime.datetime.now().strftime('%s'))
		apitoken.save()
		user = User.objects.get(pk=apitoken.user_id)
		return user        
	except:
		return False

def control_is_authenticated(bundle, **kwargs):
	##Check if the user exists
	token = bundle.META.get("HTTP_X_AUTH_TOKEN")
	try: 
		apitoken = ApiToken.objects.get(token = token)
		if apitoken.remember and apitoken.last_js + 7776000 < long(datetime.datetime.now().strftime('%s')):
			return False
		elif not apitoken.remember and apitoken.last_js + 900 < long(datetime.datetime.now().strftime('%s')):
			return False

		apitoken.last_js = int(datetime.datetime.now().strftime('%s'))
		apitoken.save()
		user = User.objects.get(pk=apitoken.user_id)
		return user        
	except:
		return False

def logout(bundle):
	try:    
		apitoken = ApiToken.objects.get(token = bundle.META.get("HTTP_X_AUTH_TOKEN"), user_id = bundle.user.pk)    
		apitoken.delete()
		return True
	except:
		return False

def delete_account(user=None):
	# If the user exists
	if user and User.objects.get(pk = user.id):
		# 1) delete profile
		# 2) delete wings
		# 3) delete notifications
		# 4) delete account
		account = User.objects.get(pk = user.id)
		account.is_active = False
		account.save()
		# 5) delete tokens
		token = ApiToken.objects.filter(user_id = user.id)
		token.delete()
	return

def forgot_password(user, backend, **kwargs):
	if user and User.objects.get(pk = user.id):
		backend = get_backend(backend)
		sent = backend.forgot_password(user, **kwargs)
		if sent:
			return True
	return False

def check_forgot_token(filters, backend):
	backend = get_backend(backend)
	return backend.check_forgot_token(filters)

def change_password(new_password, forgot_token):
	try:
		reg = RegistrationProfile.objects.get(activation_key = forgot_token)
		reg.activation_key = 'ALREADY_ACTIVATED'
		reg.save()
		user = User.objects.get(pk = reg.user_id)
		user.set_password(new_password)
		user.is_active = True
		user.save()
	except:
		raise NotAKey()
	
	
