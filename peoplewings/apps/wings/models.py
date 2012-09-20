from django.db import models
from people.models import PW_STATE_CHOICES, UserProfile
from locations.models import City

max_text_msg_len = 1000
max_short_text_len = 200
max_ultra_short_len = 10

BETTER_DAYS_CHOICES = (
    ('A', 'Any'),
    ('F', 'From Monday to Friday'),
    ('T', 'From Monday to Thursday'),
    ('W', 'Weekend'),
)

WHERE_SLEEPING_CHOICES = (
    ('C', 'Common area'),
    ('P', 'Private area'),
    ('S', 'Shared private area'),
)

SMOKING_CHOICES = (
    ('S', 'I smoke'),
    ('D', 'I don\'t smoke, but guests can smoke here'),
    ('N', 'No smoking allowed'),
)
WING_STATUS = (
    ('Y', 'Yes'),
    ('N', 'No'),
    ('M', 'Maybe'),
    ('C', 'Coffe or drink'),
    ('T', 'Traveling'),
    ('B', 'By wing')
) 

CAPACITY_OPTIONS=[(str(i), str(i)) for i in range(1, 10)]
CAPACITY_OPTIONS.append(('m', '+9'))

# Wing class
class Wing(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=max_short_text_len, unique=False)
    status = models.CharField(max_length=1, choices=WING_STATUS, default='Y', verbose_name='Wing status')
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    best_days = models.CharField(max_length=1, choices=BETTER_DAYS_CHOICES, default='A', verbose_name='Better days to host')
    is_request = models.BooleanField(default=False, verbose_name='Are you requesting a wing?')
    
# Accomodation wing class
class Accomodation(Wing):
    sharing_once = models.BooleanField(default=False, verbose_name='Are you sharing for one time?')
    capacity = models.CharField(max_length=1, choices=CAPACITY_OPTIONS, default=0)
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
    about = models.TextField(max_length=max_text_msg_len, blank=True, verbose_name='About your Accomodation')
    address = models.CharField(max_length=max_short_text_len, blank=True, verbose_name='Street address')
    number = models.CharField(max_length=max_ultra_short_len, blank=True)
    additional_information = models.TextField(max_length=max_text_msg_len, blank=True)   
    postal_code = models.CharField(max_length=max_short_text_len, blank=True, verbose_name='ZIP / Postal code')
    city = models.ForeignKey(City, on_delete=models.PROTECT)
