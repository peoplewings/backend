from django.db import models
from people.models import PW_STATE_CHOICES, max_long_len, max_medium_len, max_short_len, City, UserProfile

BETTER_DAYS_CHOICES = (
    ('F', 'From Monday to Friday'),
    ('T', 'From Monday to Thursday'),
    ('W', 'Weekend'),
    ('A', 'Any'),
)

WHERE_SLEEPING_CHOICES = (
    ('C', 'Common area'),
    ('P', 'Private area'),
    ('S', 'Shared private area'),
)

SMOKING_CHOICES = (
    ('S', 'I smoke'),
    ('D', 'I don\'t smoke'),
    ('N', 'No smoking allowed'),
)

# Create your models here.
class Wing(models.Model):
	author = models.ForeignKey(UserProfile)
	name = models.CharField(max_length=max_medium_len, verbose_name='Wing name')
	status = models.CharField(max_length=1, choices=PW_STATE_CHOICES, default='Y', verbose_name='Wing status')
	sharing_once = models.BooleanField(default=False, verbose_name='Are you sharing for one time?')
	from_date = models.DateField(verbose_name='From', null=True, blank=True)
	to_date = models.DateField(verbose_name='To', null=True, blank=True)
	better_days = models.CharField(max_length=1, choices=BETTER_DAYS_CHOICES, default='A', verbose_name='Better days to host')

	capacity = models.CharField(max_length=1, choices=[(str(i), str(i)) for i in range(1, 10)], default=0)

	preferred_gender = models.CharField(max_length=1)
	wheelchair = models.BooleanField(default=False, verbose_name='Wheelchair accessible')
	where_sleeping_type = models.CharField(max_length=1, choices=WHERE_SLEEPING_CHOICES, default='C', verbose_name='Sleeping arrangements')
	smoking = models.CharField(max_length=1, choices=SMOKING_CHOICES, default='N')
	i_have_pet = models.BooleanField(default=False)
	pets_allowed = models.BooleanField(default=False, verbose_name='Guests pets allowed')
	blankets = models.BooleanField(default=False, verbose_name='I have blankets')
	live_center = models.BooleanField(default=False, verbose_name='I live in the center')
	underground = models.BooleanField(default=False)
	bus = models.BooleanField(default=False)
	tram = models.BooleanField(default=False)
	train = models.BooleanField(default=False)
	others = models.BooleanField(default=False)
	about = models.CharField(max_length=max_long_len, null=True, blank=True, verbose_name='About your Accomodation')	
	#where_sleeping_description = models.CharField(max_length=max_long_len, null=True, blank=True)	
	address = models.CharField(max_length=max_medium_len, null=True, blank=True, verbose_name='Street address')
	number = models.PositiveIntegerField(default=0)
	additional_information = models.CharField(max_length=max_long_len, null=True, blank=True)
	city = models.ForeignKey(City, null=True)	
	postal_code = models.CharField(max_length=max_short_len, null=True, blank=True, verbose_name='ZIP / Postal code')

