import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from peoplewings.apps.registration import signals
from peoplewings.apps.registration.forms import RegistrationForm
from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.exceptions import  NotAKey
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.validators import email_re


import random


class CustomBackend(object):
	"""
	A registration backend which follows a simple workflow:

	1. User signs up, inactive account is created.

	2. Email is sent to user with activation link.

	3. User clicks activation link, account is now active.

	Using this backend requires that

	* ``registration`` be listed in the ``INSTALLED_APPS`` setting
	  (since this backend makes use of models defined in this
	  application).

	* The setting ``ACCOUNT_ACTIVATION_DAYS`` be supplied, specifying
	  (as an integer) the number of days from registration during
	  which a user may activate their account (after that period
	  expires, activation will be disallowed).

	* The creation of the templates
	  ``registration/activation_email_subject.txt`` and
	  ``registration/activation_email.txt``, which will be used for
	  the activation email. See the notes for this backends
	  ``register`` method for details regarding these templates.

	Additionally, registration can be temporarily closed by adding the
	setting ``REGISTRATION_OPEN`` and setting it to
	``False``. Omitting this setting, or setting it to ``True``, will
	be interpreted as meaning that registration is currently open and
	permitted.

	Internally, this is accomplished via storing an activation key in
	an instance of ``registration.models.RegistrationProfile``. See
	that model and its custom manager for full documentation of its
	fields and supported operations.
	
	"""
	def register(self, request, **kwargs):
		"""
		Given a username, email address and password, register a new
		user account, which will initially be inactive.

		Along with the new ``User`` object, a new
		``registration.models.RegistrationProfile`` will be created,
		tied to that ``User``, containing the activation key which
		will be used for this account.

		An email will be sent to the supplied email address; this
		email should contain an activation link. The email will be
		rendered using two templates. See the documentation for
		``RegistrationProfile.send_activation_email()`` for
		information about these templates and the contexts provided to
		them.

		After the ``User`` and ``RegistrationProfile`` are created and
		the activation email is sent, the signal
		``registration.signals.user_registered`` will be sent, with
		the new ``User`` as the keyword argument ``user`` and the
		class of this backend as the sender.

		"""
	   
		username, email, password, last_name, first_name = kwargs['username'], kwargs['email'], kwargs['password'], kwargs['lastName'], kwargs['firstName']
		site = settings.SITE
		# username = kwargs['first_name'] + "." + kwargs['last_name'] 
		new_user = RegistrationProfile.objects.create_inactive_user(username, email, password, site)		
									
		signals.user_registered.send(sender=self.__class__,
									 user=new_user,
									 request=request,
									 lastname=last_name, 
									 firstname=first_name)
		return new_user

	def activate(self, request, activation_key):
		"""
		Given an an activation key, look up and activate the user
		account corresponding to that key (if possible).

		After successful activation, the signal
		``registration.signals.user_activated`` will be sent, with the
		newly activated ``User`` as the keyword argument ``user`` and
		the class of this backend as the sender.
		
		"""
		activated = RegistrationProfile.objects.activate_user(activation_key)
		if activated:
			signals.user_activated.send(sender=self.__class__,
										user=activated,
										request=request)
		return activated

	def registration_allowed(self, request):
		"""
		Indicate whether account registration is currently permitted,
		based on the value of the setting ``REGISTRATION_OPEN``. This
		is determined as follows:

		* If ``REGISTRATION_OPEN`` is not specified in settings, or is
		  set to ``True``, registration is permitted.

		* If ``REGISTRATION_OPEN`` is both specified and set to
		  ``False``, registration is not permitted.
		
		"""
		return getattr(settings, 'REGISTRATION_OPEN', True)

	def get_form_class(self, request):
		"""
		Return the default form class used for user registration.
		
		"""
		return RegistrationForm

	def post_registration_redirect(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		user registration.
		
		"""
		return ('registration_complete', (), {})

	def post_activation_redirect(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		account activation.
		
		"""
		return ('registration_activation_complete', (), {})

	def forgot_password(self, request, **kwargs):
						   
		site = settings.SITE
		
		sent = RegistrationProfile.objects.create_forgot_user(request.user, site)
		return sent

	def check_forgot_token(self, filters):
	   
		try:
			reg = RegistrationProfile.objects.get(activation_key = filters.get('forgotToken'))
			if reg.key_timestamp + datetime.timedelta(hours=24*7) > datetime.datetime.utcnow().replace(tzinfo=utc):
				return True
			else:
				return False
		except:
			raise NotAKey()

class AuthMailBackend(ModelBackend):
	def authenticate(self, username=None, password=None):
		if email_re.search(username):
			try:
				user = User.objects.get(email=username)
				if user.check_password(password):
					return user
			except User.DoesNotExist:
				return None
		return None




