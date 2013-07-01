import datetime
import time
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from peoplewings.apps.registration.exceptions import ActivationCompleted, NotAKey, KeyExpired, ExistingUser
from peoplewings.apps.registration.signals import user_deleted, user_registered


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):

	def activate_user(self, activation_key):
		# Make sure the key we're trying conforms to the pattern of a
		# SHA1 hash; if it doesn't, no point trying to look it up in
		# the database.
		if SHA1_RE.search(activation_key):
			try:
				profile = self.get(activation_key=activation_key)
			except self.model.DoesNotExist:
				raise ActivationCompleted()
			if not profile.activation_key_expired():
				user = profile.user
				user.is_active = True
				user.save()
				profile.activation_key = self.model.ACTIVATED
				profile.save()
				return user
			else:
				raise KeyExpired()
		else:
			raise NotAKey()
		return False
	
	def create_inactive_user(self, username, email, password, site, send_email=True):
		import pdb; pdb.set_trace()
		try:
			user = User.objects.filter(email=email)
		except Exception:
			pass
		if user:
			raise ExistingUser

		new_user = User.objects.create_user(username, email, password)
		new_user.is_active = False
		new_user.save()

		registration_profile = self.create_profile(new_user)

		if send_email:
			registration_profile.send_activation_email(site)

		return new_user
	create_inactive_user = transaction.commit_on_success(create_inactive_user)

	def create_profile(self, user):

		salt = sha_constructor(str(random.random())).hexdigest()[:5]
		username = user.username
		if isinstance(username, unicode):
			username = username.encode('utf-8')
		activation_key = sha_constructor(salt+username).hexdigest()
		return self.create(user=user, activation_key=activation_key)

	def update_profile(self, user):

		salt = sha_constructor(str(random.random())).hexdigest()[:5]
		username = user.username
		if isinstance(username, unicode):
			username = username.encode('utf-8')
		activation_key = sha_constructor(salt+username).hexdigest()
		try:        
			previous = RegistrationProfile.objects.get(user=user)
			previous.delete()            
		except:
			pass           
		return self.create(user=user, activation_key=activation_key)
		
	def delete_expired_users(self):

		for profile in self.all():
			if profile.activation_key_expired():
				user = profile.user
				if not user.is_active:
					user.delete()

	def create_forgot_user(self, user, site):
		registration_profile = self.update_profile(user)
		sent = registration_profile.send_forgot_email(site, user)

		return sent


class RegistrationProfile(models.Model):

	ACTIVATED = u"ALREADY_ACTIVATED"
	
	user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
	activation_key = models.CharField(_('activation key'), max_length=40)
	key_timestamp = models.DateTimeField(auto_now_add = True, null=True)
	
	objects = RegistrationManager()
	
	class Meta:
		verbose_name = _('registration profile')
		verbose_name_plural = _('registration profiles')
	
	def __unicode__(self):
		return u"Registration information for %s" % self.user
	
	def activation_key_expired(self):

		expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
		return self.activation_key == self.ACTIVATED or (self.user.date_joined + expiration_date <= datetime.datetime.utcnow().replace(tzinfo=utc))
	activation_key_expired.boolean = True

	def send_activation_email(self, site, kind='None'):
		ctx_dict = {'activation_key': self.activation_key, 'site': site}
		subject = render_to_string('registration/activation_email_subject.txt', ctx_dict)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		
		message = render_to_string('registration/activation_email.txt', ctx_dict)
		send_mail(subject, message, settings.REGISTER_SERVER_EMAIL, [self.user.email], fail_silently=False, auth_user=settings.REGISTER_EMAIL_HOST_USER)
		return True

	def send_forgot_email(self, site, user):
		
		ctx_dict = {'reset_token': self.activation_key,
					'email_user': user.email,
					'site': site}
		subject = render_to_string('registration/forgot_password_email_subject.txt', ctx_dict)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		
		message = render_to_string('registration/forgot_email.txt', ctx_dict)
		
		send_mail(subject, message, settings.FORGOT_SERVER_EMAIL, [self.user.email], fail_silently=False, auth_user=settings.FORGOT_EMAIL_HOST_USER)
		return True

	@staticmethod
	def cron_delete_inactive_accounts():
		import datetime
		from django.contrib.auth.models import User
		from registration.models import RegistrationProfile
		from people.models import UserProfile
		from django.db.models import Q
		try:
			accounts = RegistrationProfile.objects.exclude(Q(activation_key__icontains='ACTIV')&Q(key_timestamp__gt=datetime.datetime.now() - datetime.timedelta(days=7)))
			for i in accounts:
				user_account = User.objects.get(pk=i.user_id)
				if user_account and user_account.date_joined == user_account.last_login:
					i.delete()
					prof = UserProfile.objects.get(user= user_account)
					prof.delete()
					user_account.delete()
		except:
			pass
class FacebookUser(models.Model):  
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	fbid = models.CharField(max_length=75)

class TermsAndConditions(models.Model):	
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	email = models.CharField(max_length=75)
	registration_date = models.BigIntegerField()
	deletion_date = models.BigIntegerField(null=True)
	has_accepted = models.BooleanField(default=False)
	
def createTermsAndConditions(sender, user, request, **kwargs):	
	
	terms = TermsAndConditions.objects.filter(user=user)
	if len(terms) == 0:
		terms = TermsAndConditions.objects.create(user=user, email= user.email, registration_date= time.time(), deletion_date = None, has_accepted= True)
		terms.save()

def updateTermsAndConditions(sender, request, **kwargs):
	terms = TermsAndConditions.objects.filter(user=user)
	if len(terms) == 1:
		terms.user = None
		terms.deletion_date = time.time()
		terms.save()

user_registered.connect(createTermsAndConditions)
user_deleted.connect(updateTermsAndConditions)
