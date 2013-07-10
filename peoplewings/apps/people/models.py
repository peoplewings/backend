from django.db import models, connection, transaction
from django.contrib.auth.models import User
from signals import user_deleted
from django.utils import timezone
from datetime import date, datetime
from peoplewings.apps.registration.signals import user_registered
from peoplewings.apps.people.signals import profile_created
from peoplewings.apps.registration.forms import RegistrationForm
from peoplewings.apps.cropper.models import Cropped
from peoplewings.apps.locations.models import City
from peoplewings.global_vars import *
from django.conf import settings as django_settings
from django_extensions.db.fields import UUIDField

# SOCIAL NETWORK
class SocialNetwork(models.Model):
	name = models.CharField(max_length=max_medium_len, unique=True)  

class UserSocialNetwork(models.Model):
	user_profile = models.ForeignKey('UserProfile')
	social_network = models.ForeignKey('SocialNetwork')
	social_network_username = models.CharField(max_length=max_medium_len)

# INSTANT MESSAGE
class InstantMessage(models.Model):
	name = models.CharField(max_length=max_medium_len, unique=True)  

class UserInstantMessage(models.Model):
	user_profile = models.ForeignKey('UserProfile')
	instant_message = models.ForeignKey('InstantMessage')
	instant_message_username = models.CharField(max_length=max_medium_len)

# LANGUAGE
class Language(models.Model):
	name = models.CharField(max_length=max_medium_len, unique=True)

class UserLanguage(models.Model):
	user_profile = models.ForeignKey('UserProfile')
	language = models.ForeignKey('Language')
	level = models.CharField(max_length=100, choices=LANGUAGES_LEVEL_CHOICES)

	class Meta:
		unique_together = ("user_profile", "language")

# UNIVERSITY
class University(models.Model):
  name = models.CharField(max_length=max_medium_len, unique=True)

class UserProfileStudiedUniversity(models.Model):
	user_profile = models.ForeignKey('UserProfile')
	university = models.ForeignKey('University')

class Interests(models.Model):
	gender = models.CharField(max_length = 6, choices = PREFERRED_GENDER_CHOICES, unique = True)

class UserProfile(models.Model):

	user = models.ForeignKey(User, unique=True)
	pw_state = models.CharField(max_length=100, choices=PW_STATE_CHOICES)

	avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_BIG) #175x175
	medium_avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_BIG, blank = True) # 175x175
	thumb_avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_AVATAR, blank = True) # 65x65
	blur_avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_BLUR, blank = True) # Not used
	avatar_updated = models.BooleanField(default=False)
	relationships = models.ManyToManyField("self", symmetrical=False, through='Relationship')##not used
	references = models.ManyToManyField("self", symmetrical=False, through='Reference', related_name="references+")##not used
	
	# In Basic Information
	birthday = models.DateField(verbose_name='birthday', null=True, blank=True)
	show_birthday = models.CharField(verbose_name='', max_length=100, choices=SHOW_BIRTHDAY_CHOICES, default='F')
	gender = models.CharField(verbose_name='I am', max_length=6, choices=GENDER_CHOICES, default='Male')
	interested_in = models.ManyToManyField(Interests, null=True, default = None)
	civil_state = models.CharField(verbose_name="Relationship status", max_length=2, choices=CIVIL_STATE_CHOICES, default='', blank=True, null=True)
	languages = models.ManyToManyField(Language, through='UserLanguage', null=True)

	# Locations
	current_city = models.ForeignKey(City, related_name='cc+', null=True)
	hometown = models.ForeignKey(City, related_name='ht+', null=True)
	other_locations = models.ManyToManyField(City, related_name='ol+', null=True)
	last_login = models.ForeignKey(City, related_name='ll+', null=True)

	# Contact info
	emails = models.EmailField(blank=True, max_length=100)
	phone = models.CharField(max_length=100, blank=True)
	social_networks = models.ManyToManyField(SocialNetwork, through='UserSocialNetwork')
	instant_messages = models.ManyToManyField(InstantMessage, through='UserInstantMessage')

	# About me
	all_about_you = models.TextField(max_length=500, blank=True)
	main_mission = models.TextField(max_length=100, blank=True, verbose_name='Current mission')
	occupation = models.CharField(max_length=500, blank=True)
	company = models.CharField(max_length=100, blank=True, verbose_name='Companies')
	universities = models.ManyToManyField(University, through='UserProfileStudiedUniversity')
	personal_philosophy = models.TextField(max_length=1000, blank=True)
	political_opinion = models.CharField(max_length=500, blank=True, verbose_name='Political views')
	religion = models.CharField(max_length=500, blank=True)

	# Likes
	enjoy_people = models.TextField(verbose_name="People I enjoy", max_length=500, blank=True)
	# peliculas, libros, series, videojuegos, musica
	movies = models.TextField(verbose_name="Likes", max_length=500, blank=True)
	# deportes y actividades favoritas
	sports = models.TextField(max_length=500, blank=True)
	other_pages = models.TextField(verbose_name="Likes", max_length=500, blank=True)    
	# que te gusta compartir o ensenyar
	sharing = models.TextField(verbose_name="Show, learn, share...", max_length=1000, blank=True)
	# cosas increibles que hayas hecho o visto
	incredible = models.TextField(verbose_name="Amazing things done/seen", max_length=1000, blank=True)
	inspired_by = models.TextField(verbose_name="People who inspires you", max_length=500, blank=True)
	# citas
	quotes = models.TextField(verbose_name="Favorite quotations", max_length=500, blank=True)
	# opinion sobre peoplewings
	pw_opinion = models.TextField(verbose_name="Your opinion please", max_length=500, blank=True) 

	# Trips
	places_lived_in = models.TextField(max_length=max_long_len, blank=True)
	places_visited = models.TextField(max_length=max_long_len, blank=True)    
	places_gonna_go = models.TextField(max_length=max_long_len, blank=True)
	places_wanna_go = models.TextField(max_length=max_long_len, blank=True)

	#Reply rate (between 0 and 1)
	reply_rate = models.IntegerField(default=-1)
	#Reply time
	reply_time = models.BigIntegerField(default=-1)

	active = models.BooleanField(default=True)


	def get_age(self):			
		today = date.today()
		age = today.year - self.birthday.year
		if today.month < self.birthday.month or (today.month == self.birthday.month and today.day < self.birthday.day): age -= 1
		return age

	def __unicode__(self):
		return unicode(self.user.email)
	
	@staticmethod
	@transaction.commit_manually
	def cron_reply_rate():
		cur = connection.cursor()
		cur.callproc('batch_reply_rate', ())		
		cur.close()
		transaction.commit()

class Relationship(models.Model):    
	sender = models.ForeignKey('UserProfile', related_name='sender')
	receiver = models.ForeignKey('UserProfile', related_name='receiver')
	relationship_type = models.CharField(max_length=8, choices=RELATIONSHIP_CHOICES)
	fuck_you = models.CharField(max_length=8, choices=RELATIONSHIP_CHOICES, null=True)

	class Meta:
		unique_together = ("sender", "receiver")


class Reference(models.Model):    
	author = models.ForeignKey('UserProfile', related_name='author')
	commented = models.ForeignKey('UserProfile', related_name='commented')
	title = models.CharField(max_length=max_medium_len)
	text = models.TextField(max_length=max_500_char)
	punctuation = models.CharField(max_length=8, choices=PUNCTUATION_CHOICES)

def createUserProfile(sender, user, request, **kwargs):    
	if UserProfile.objects.filter(user= user).count() == 0:
		form = RegistrationForm(request.POST)
		registered_user = User.objects.get(username=user.username)
		registered_user.last_name = kwargs['lastname']
		registered_user.first_name = kwargs['firstname']
		registered_user.is_active=False
		registered_user.save()
		data = UserProfile.objects.create(pk=user.pk, user=user)
		data.gender = form.data["gender"]
		data.birthday = datetime(year=int(form.data["birthdayYear"]), month=int(form.data["birthdayMonth"]), day=int(form.data["birthdayDay"]))
		# data.birthday = form.data['birthday'] #this should work try it!
		today = date.today()
		age = today.year - data.birthday.year
		if today.month < data.birthday.month or (today.month == data.birthday.month and today.day < data.birthday.day): age -= 1
		PhotoAlbums.objects.create(name='default', author=data)
		data.save()

		#Create the welcome notification....
		try:
			profile_created.send_robust(sender=data.__class__, profile=data, first_name=kwargs['firstname'])
		except Exception, e:
			print 'WELCOME MSG FROM NORMAL CREATION ERROR ', e


def deleteUserProfile(sender, request, **kwargs):
	prof = request.user.get_profile()
	prof.delete()

class PhotoAlbums(models.Model):    
	album_id = UUIDField(auto=True, unique=True, primary_key=True, null = False)
	author = models.ForeignKey('UserProfile', related_name='photoalbums_author')
	name = models.CharField(max_length=300, default='default')
	ordering = models.IntegerField(default=1000)

class Photos(models.Model):
	photo_id = UUIDField(auto=True, unique=True, primary_key=True, null = False)
	author = models.ForeignKey('UserProfile', related_name='photos_author')
	album = models.ForeignKey('PhotoAlbums', related_name='album')
	big_url = models.CharField(max_length=500, default='')
	thumb_url = models.CharField(max_length=500, default='')
	ordering = models.IntegerField(default=1000)
	add_notificated = models.BooleanField(default=False)
	photo_hash = models.CharField(max_length=30 , default = '')

user_registered.connect(createUserProfile)
user_deleted.connect(deleteUserProfile)

from django.core.management import setup_environ
from peoplewings import settings
setup_environ(settings)
