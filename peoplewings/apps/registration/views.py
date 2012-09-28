"""
Views which allow users to create and activate accounts.

"""
import random

from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login, authenticate
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.registration.backends import get_backend
from peoplewings.apps.registration.exceptions import NotActive, AuthFail
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
    request.POST['password2'] = request.POST['password1']
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

def do_login(**kwargs):
    user = authenticate(username=kwargs['username'], password=kwargs['password'])
    if user:
        if user.is_active:
            login(request, user)
            return user
        else:
            raise NotActive()
    else:
        raise AuthFail()

def login(bundle):
    ## Checks if the user/pass is valid
    user = do_login(request = bundle, username = bundle.data['username'], password = bundle.data['password'])
    ## Creates a new ApiToken to simulate a session. The ApiToken is totally empty
    api_token = ApiToken.objects.create()
    ## Links the user to the token
    api_token.save(user=user)
    return api_token.token
    
    
    
