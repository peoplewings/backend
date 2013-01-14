from django.db import models
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.locations.models import City

from peoplewings.global_vars import *

from pprint import pprint

# Wing class
class Wing(models.Model):
	author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	name = models.CharField(max_length=max_short_text_len, unique=False, default="Wing")
	status = models.CharField(max_length=1, choices=WINGS_STATUS, default='Y', verbose_name='Wing status')
	date_start = models.DateField(null=True)
	date_end = models.DateField(null=True)
	best_days = models.CharField(max_length=1, choices=BETTER_DAYS_CHOICES, default='A', verbose_name='Better days to host')
	is_request = models.BooleanField(default=False, verbose_name='Are you requesting a wing?') # True => Applicant, False => Host
	city = models.ForeignKey(City, on_delete=models.PROTECT)

	def get_type(self):
		if Accomodation.objects.filter(pk=self.pk).exists(): return Accomodation.objects.get(pk=self.pk).get_type()

	def get_class_name(self):
		if Accomodation.objects.filter(pk=self.pk).exists(): return 'Accomodation'
	
	
class PublicTransport(models.Model):
	name = models.CharField(max_length=50, blank = False, null = False, default = 'Not specified')

# Accomodation wing class
class Accomodation(Wing):
	sharing_once = models.BooleanField(default=False, verbose_name='Are you sharing for one time?')
	capacity = models.CharField(max_length=1, choices=CAPACITY_OPTIONS, default=1)
	preferred_male = models.BooleanField(default=False)
	preferred_female = models.BooleanField(default=False)
	wheelchair = models.BooleanField(default=False, verbose_name='Wheelchair accessible')
	where_sleeping_type = models.CharField(max_length=1, choices=WHERE_SLEEPING_CHOICES, default='C', verbose_name='Sleeping arrangements')
	smoking = models.CharField(max_length=1, choices=SMOKING_CHOICES, default='N')
	i_have_pet = models.BooleanField(default=False)
	pets_allowed = models.BooleanField(default=False, verbose_name='Guests pets allowed')
	blankets = models.BooleanField(default=False, verbose_name='I have blankets')
	live_center = models.BooleanField(default=False, verbose_name='I live in the center')
	public_transport = models.ManyToManyField(PublicTransport)
	about = models.TextField(max_length=max_text_msg_len, blank=True, verbose_name='About your Accomodation')
	address = models.CharField(max_length=max_short_text_len, blank=True, verbose_name='Street address')
	number = models.CharField(max_length=max_ultra_short_len, blank=True)
	additional_information = models.TextField(max_length=max_text_msg_len, blank=True)   
	postal_code = models.CharField(max_length=max_short_text_len, blank=True, verbose_name='ZIP / Postal code') 
