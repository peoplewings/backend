from django.db import models
from django.contrib.auth.models import User
from signals import user_deleted
from django.utils import timezone
from datetime import date, datetime
from peoplewings.apps.registration.signals import user_registered
from peoplewings.apps.registration.forms import RegistrationForm
from peoplewings.apps.cropper.models import Cropped
from peoplewings.apps.locations.models import City
from peoplewings.global_vars import *

# SOCIAL NETWORK
class SocialNetwork(models.Model):
    name = models.CharField(max_length=max_short_len, unique=True)  

class UserSocialNetwork(models.Model):
    user_profile = models.ForeignKey('UserProfile')
    social_network = models.ForeignKey('SocialNetwork')
    social_network_username = models.CharField(max_length=max_short_len)

# INSTANT MESSAGE
class InstantMessage(models.Model):
    name = models.CharField(max_length=max_short_len, unique=True)  

class UserInstantMessage(models.Model):
    user_profile = models.ForeignKey('UserProfile')
    instant_message = models.ForeignKey('InstantMessage')
    instant_message_username = models.CharField(max_length=max_short_len)
"""
# CITY (old version)
class City(models.Model):
    #latitude = models.DecimalField(max_digits=11, decimal_places=9)
    #longitude = models.DecimalField(max_digits=12, decimal_places=9)
    country = models.CharField(max_length=max_medium_len)
    state = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    cid = models.CharField(max_length=40, unique=True)
"""

# LANGUAGE
class Language(models.Model):
    name = models.CharField(max_length=max_short_len, unique=True)  

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
    degree = models.CharField(max_length=max_medium_len, blank=True)

class Interests(models.Model):
    gender = models.CharField(max_length = 6, choices = GENDER_CHOICES, unique = True)

class UserProfile(models.Model):

    """
    Atributes of fields:
    - blank=True allows empty values for that field
    - Null=True stores these empty values as Null
    Campos requeridos: birthday, gender, pw state (default = No)
    Campos opcionales: interested in, civil state, city, all about you, main mission, occupation
    defaults: pw state = No, 
    max length: 250 => all about you, main mission, 
                20 => occupation, city
    """
    
    user = models.ForeignKey(User, unique=True)
    age = models.IntegerField(default=0)
    name_to_show = models.CharField(max_length=max_short_len, default='name_to_show')
    pw_state = models.CharField(max_length=100, choices=PW_STATE_CHOICES)
    avatar = models.CharField(max_length=max_long_len, default='/static/img/blank_avatar.jpg')

    # In Basic Information
    birthday = models.DateField(verbose_name='birthday', null=True) #Don't know why!
    show_birthday = models.CharField(verbose_name='', max_length=100, choices=SHOW_BIRTHDAY_CHOICES, default='F')
    gender = models.CharField(verbose_name='I am', max_length=6, choices=GENDER_CHOICES, default='Male')
    interested_in = models.ManyToManyField(Interests, null=True, default = None)
    civil_state = models.CharField(verbose_name="Relationship status", max_length=2, choices=CIVIL_STATE_CHOICES, default='', blank=True, null=True)
    languages = models.ManyToManyField(Language, through='UserLanguage', null=True)

    # Locations
    current_city = models.ForeignKey(City, related_name='cc+', null=True)
    hometown = models.ForeignKey(City, related_name='ht+', null=True)
    other_locations = models.ManyToManyField(City, related_name='ol+', null=True)

    # Contact info
    emails = models.EmailField(blank=True)
    phone = models.CharField(max_length=max_short_len, blank=True)
    social_networks = models.ManyToManyField(SocialNetwork, through='UserSocialNetwork')
    instant_messages = models.ManyToManyField(InstantMessage, through='UserInstantMessage')

    # About me
    all_about_you = models.TextField(max_length=max_long_len, blank=True)
    main_mission = models.TextField(max_length=max_long_len, blank=True, verbose_name='Current mission')
    occupation = models.CharField(max_length=max_short_len, blank=True)
    company = models.CharField(max_length=max_short_len, blank=True, verbose_name='Companies')
    universities = models.ManyToManyField(University, through='UserProfileStudiedUniversity')
    personal_philosophy = models.TextField(max_length=max_long_len, blank=True)
    political_opinion = models.CharField(max_length=max_short_len, blank=True, verbose_name='Political views')
    religion = models.CharField(max_length=max_short_len, blank=True)

    # Likes
    enjoy_people = models.TextField(verbose_name="People I enjoy", max_length=max_long_len, blank=True)
    # peliculas, libros, series, videojuegos, musica
    movies = models.TextField(verbose_name="Likes", max_length=max_long_len, blank=True)
    # deportes y actividades favoritas
    sports = models.TextField(max_length=max_long_len, blank=True)
    other_pages = models.TextField(verbose_name="Likes", max_length=max_long_len, blank=True)    
    # que te gusta compartir o ensenyar
    sharing = models.TextField(verbose_name="Show, learn, share...", max_length=max_long_len, blank=True)
    # cosas increibles que hayas hecho o visto
    incredible = models.TextField(verbose_name="Amazing things done/seen", max_length=max_long_len, blank=True)
    inspired_by = models.TextField(verbose_name="People who inspires you", max_length=max_long_len, blank=True)
    # citas
    quotes = models.TextField(verbose_name="Favorite quotations", max_length=max_long_len, blank=True)
    # opinion sobre peoplewings
    pw_opinion = models.TextField(verbose_name="Your opinion please", max_length=max_long_len, blank=True) 

    # Trips
    places_lived_in = models.TextField(max_length=max_long_len, blank=True)
    places_visited = models.TextField(max_length=max_long_len, blank=True)    
    places_gonna_go = models.TextField(max_length=max_long_len, blank=True)
    places_wanna_go = models.TextField(max_length=max_long_len, blank=True) 

    # a anyadir en el futuro
    #relationships = models.ManyToManyField("self", symmetrical=False, through='Relationship')

"""
class Relationship(models.Model):

    RELATIONSHIP_CHOICES = (
        ('F', 'Friend'),
        ('P', 'Pendent'),
        ('B', 'Blocked'),
        ('R', 'Rejected'),
    )
    relationship_type = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES, null=True)
    user1 = models.ForeignKey('UserProfile', related_name='r1')
    user2 = models.ForeignKey('UserProfile', related_name='r2')
"""

def createUserProfile(sender, user, request, **kwargs):  
    form = RegistrationForm(request.POST)
    registered_user = User.objects.get(username=user.username)
    registered_user.last_name = kwargs['lastname']
    registered_user.first_name = kwargs['firstname']
    registered_user.is_active=False
    registered_user.save()
    data = UserProfile.objects.create(user=user, name_to_show=kwargs['firstname'])
    data.gender = form.data["gender"]
    data.birthday = datetime(year=int(form.data["birthday_year"]), month=int(form.data["birthday_month"]), day=int(form.data["birthday_day"]))
    # data.birthday = form.data['birthday'] #this should work try it!
    today = date.today()
    age = today.year - data.birthday.year
    if today.month < data.birthday.month or (today.month == data.birthday.month and today.day < data.birthday.day): age -= 1
    data.age = age
    data.save()

def deleteUserProfile(sender, request, **kwargs):
    prof = request.user.get_profile()
    prof.delete()
  

user_registered.connect(createUserProfile)
user_deleted.connect(deleteUserProfile)

from django.core.management import setup_environ
from peoplewings import settings
setup_environ(settings)
