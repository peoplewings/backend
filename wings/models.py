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

# Create your models here.
class Wing(models.Model):
	author = models.ForeignKey(UserProfile)
	status = models.CharField(max_length=1, choices=PW_STATE_CHOICES, default='N')
	from_date = models.DateField(verbose_name='From', null=True)
	to_date = models.DateField(verbose_name='To', null=True)
	better_days = models.CharField(max_length=1, choices=BETTER_DAYS_CHOICES, default='A')
	max_pw = models.IntegerField(default=0)
	preferred_gender = models.CharField(max_length=1, default='B')
	wheelchair = models.BooleanField(default=True)
	smoking = models.BooleanField(default=True)
	i_have_pets = models.BooleanField(default=True)
	pets_allowed = models.BooleanField(default=True)
	live_center = models.BooleanField(default=True)
	public_transports = models.CharField(max_length=max_long_len, null=True, blank=True)
	blankets = models.BooleanField(default=True)
	about = models.CharField(max_length=max_long_len, null=True, blank=True)
	where_sleeping_type = models.CharField(max_length=1, choices=WHERE_SLEEPING_CHOICES, default='C')
	where_sleeping_description = models.CharField(max_length=max_long_len, null=True, blank=True)
	city = models.ForeignKey(City, null=True, blank=True)
	address = models.CharField(max_length=max_medium_len, null=True, blank=True)
	number = models.PositiveIntegerField(default=0)
	additional_information = models.CharField(max_length=max_long_len, null=True, blank=True)
	postal_code = models.CharField(max_length=max_short_len, null=True, blank=True)