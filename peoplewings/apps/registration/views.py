"""
Views which allow users to create and activate accounts.

"""
import random
import datetime
from django.utils.timezone import utc

from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login as auth_login, authenticate
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.registration.backends import get_backend
from peoplewings.apps.registration.exceptions import NotActive, AuthFail, BadParameters
from django.contrib.auth.models import User


def activate(request, backend,
             template_name='registration/activate.html',
             success_url=None, extra_context=None, **kwargs):
    backend = get_backend(backend)
    account = backend.activate(request, **kwargs)
    if account:
    ## All OK
        import pprint
        print 'Activation OK'
        pprint.pprint(account)
        return True
    ## Not OK
    print 'Activation NO'
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              kwargs,
                              context_instance=context)


def register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='registration/registration_form.html',
             extra_context=None):

    request.POST['username'] = request.POST['first_name'] + "." + str(random.getrandbits(24))
    request.POST['password2'] = request.POST['password']
    if request.POST['email'] != request.POST['repeat_email']: 
        bundle = {"email": ["Emails don't match"]}    
        raise BadParameters(bundle)
    bundle_data = request.POST
    backend = get_backend(backend)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    new_user = backend.register(request, **bundle_data)
    return   
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return form

def do_login(request, username, password):
    user = authenticate(username=username, password=password)
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
    api_token = ApiToken.objects.create(user=user)
    ## Links the user to the token
    api_token.save()
    return api_token.token

def api_token_is_authenticated(bundle, **kwargs):
    ##Check if the user exists
    token = bundle.META.get("HTTP_X_AUTH_TOKEN")
    #apitoken = ApiToken.objects.get(token = token, last > datetime.datetime.utcnow().replace(tzinfo=utc) + 3600)
    try:    
        apitoken = ApiToken.objects.get(token = token, last__gt = (datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(seconds=3600)))
        apitoken.last = datetime.datetime.utcnow().replace(tzinfo=utc)
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

def forgot_password(request, backend, **kwargs):
    if request.user and User.objects.get(pk = request.user.id):
        backend = get_backend(backend)
        sent = backend.forgot_password(request, **kwargs)
        if sent:
            return True
    return False

    
    
