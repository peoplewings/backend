from django.db import models
from django.contrib.auth.models import User
from registration.signals import user_registered
from people.signals import user_deleted
from django.utils import timezone
from datetime import date, datetime
from registration.forms import RegistrationForm

max_long_len = 250
max_short_len = 20

# LANGUAGE
class Language(models.Model):
    """
    LANGUAGES_CHOICES = (
        ('E', 'English'),
        ('S', 'Spanish'),
        ('G', 'German'),
        ('F', 'French'),
        ('C', 'Chinese'),
        ('P', 'Portuguese'),
    )
    """
    name = models.CharField(max_length=max_short_len, unique=True)  

class UserLanguage(models.Model):

    LANGUAGES_LEVEL_CHOICES = (
        ('B', 'Beginner'),
        ('I', 'Intermediate'),
        ('E', 'Expert'),
    )
    user_profile = models.ForeignKey('UserProfile')
    language = models.ForeignKey('Language')
    level = models.CharField(max_length=1, choices=LANGUAGES_LEVEL_CHOICES)

# UNIVERSITY
class University(models.Model):
  name = models.CharField(max_length=50, unique=True)

class UserProfileStudiedUniversity(models.Model):
    user_profile = models.ForeignKey('UserProfile')
    university = models.ForeignKey('University')
    degree = models.CharField(max_length=max_short_len, blank=True)


class UserProfile(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    CIVIL_STATE_CHOICES = (
        ('SI', 'Single'),
        ('EN', 'Engaged'),
        ('MA', 'Married'),
        ('WI', 'Widowed'),
        ('IR', 'In a relationship'),
        ('IO', 'In an open relationship'),
        ('IC', 'Its complicated'),
        ('DI', 'Divorced'),
        ('SE', 'Separated'),
    )
    
    PW_STATE_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('M', 'Maybe'),
        ('T', 'Traveling'),
        ('C', 'Coffee or Drink'),
    )
    
    PRIVACY_CHOICES = (
        ('M', 'Only me'),
        ('F', 'Friends'),
        ('E', 'Everybody'),
    )    

    BIRTHDAY_CHOICES = (
        ('P', 'Show month and day'),
        ('F', 'Show full'),
        ('N', 'Dont show'),
    )


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
    pw_state = models.CharField(max_length=1, choices=PW_STATE_CHOICES, default='N')

    # In Basic Information

    birthday = models.DateField(verbose_name='birthday', null=True) #Don't know why!
    show_birthday = models.CharField(verbose_name='', max_length=1, choices=BIRTHDAY_CHOICES, default='N')
    gender = models.CharField(verbose_name='I am', max_length=1, choices=GENDER_CHOICES)
    interested_in = models.CharField(max_length=1, blank=True) # he tret el null=True
    civil_state = models.CharField(verbose_name="Relationship status", max_length=2, choices=CIVIL_STATE_CHOICES, blank=True, null=True)
    languages = models.ManyToManyField(Language, through='UserLanguage')

    # Locations
    city = models.CharField(max_length=max_short_len, blank=True)
    hometown = models.CharField(max_length=max_short_len, blank=True)
    #other_locations = models.ManyToManyField(Location)

    # Contact info
    emails = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    social_networks = models.TextField(max_length=max_long_len, blank=True) # contains {social1, social2, ...}

    # About me
    all_about_you = models.TextField(max_length=max_long_len, blank=True)
    main_mission = models.TextField(max_length=max_long_len, blank=True)
    occupation = models.CharField(max_length=max_short_len, blank=True)
    company = models.CharField(max_length=max_short_len, blank=True)
    universities = models.ManyToManyField(University, through='UserProfileStudiedUniversity')
    personal_philosophy = models.TextField(max_length=max_long_len, blank=True)
    political_opinion = models.CharField(max_length=max_short_len, blank=True)
    religion = models.CharField(max_length=max_short_len, blank=True)

    # Likes
    people_you_like = models.TextField(max_length=max_long_len, blank=True)
    # peliculas, libros, series, videojuegos, musica
    favourite_movies_series_others = models.TextField(max_length=max_long_len, blank=True)
    # deportes y actividades favoritas
    favourite_sports_activities = models.TextField(max_length=max_long_len, blank=True)
    other_pages_you_like = models.TextField(max_length=max_long_len, blank=True)    
    # que te gusta compartir o ensenyar
    what_you_like_sharing = models.TextField(max_length=max_long_len, blank=True)
    # cosas increibles que hayas hecho o visto
    incredible_done_seen = models.TextField(max_length=max_long_len, blank=True)
    people_inspired_you = models.TextField(max_length=max_long_len, blank=True)
    # citas
    quotes = models.TextField(max_length=max_long_len, blank=True)
    # opinion sobre peoplewings
    pw_opinion = models.TextField(max_length=max_long_len, blank=True) 

    # Trips
    places_lived_in = models.TextField(max_length=max_long_len, blank=True)
    places_visited = models.TextField(max_length=max_long_len, blank=True)    
    places_gonna_go = models.TextField(max_length=max_long_len, blank=True)
    places_wanna_go = models.TextField(max_length=max_long_len, blank=True)    

    # a anyadir en el futuro
    #relationships = models.ManyToManyField("self", symmetrical=False, through='Relationship')
    #pic=models.ImageField(upload_to='/uploads', blank=True)

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