from django.db import models
from django.contrib.auth.models import User
from registration.signals import user_registered
from people.signals import user_deleted
from django.utils import timezone
from datetime import date, datetime
from registration.forms import RegistrationForm

class Languages(models.Model):
  name = models.CharField(max_length=30, unique=True)

class University(models.Model):
  name = models.CharField(max_length=50, unique=True)

class UserProfile(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    INTERESTED_IN_GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('B', 'Both'),
        ('N', 'None'),
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
    
    user = models.ForeignKey(User, unique=True)
    birthday = models.DateField(null=True, verbose_name='Date of birth')
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    interested_in = models.CharField(max_length=1, choices=INTERESTED_IN_GENDER_CHOICES, null=True)
    civil_state = models.CharField(max_length=2, choices=CIVIL_STATE_CHOICES, null=True)
    city = models.CharField(max_length=20)
    pw_state = models.CharField(max_length=1, choices=PW_STATE_CHOICES, null=True)
    #pic=models.ImageField(upload_to='/uploads', blank=True)
    languages = models.ManyToManyField(Languages)
    """
    lista de universidades en la que ha estudiado, separadas por comas. Por ejemplo:
    universidad de Granada, Universidad Complutense de Madrid, Universidad Autonoma de Barcelona
    """
    universities = models.ManyToManyField(University) 
    #privacy_settings = models.CharField(max_length=1, choices=PRIVACY_CHOICES, default='M')
    all_about_you = models.TextField(blank=True)
    main_mission = models.TextField(blank=True)
    occupation = models.CharField(max_length=20, blank=True)
    # experiencia sobre pw
    pw_experience = models.TextField(blank=True)
    personal_philosophy = models.TextField(blank=True)
    other_pages_you_like = models.TextField(blank=True)
    people_you_like = models.TextField(blank=True)
    # peliculas, libros, series, videojuegos, music, deportes, actividades favoritas
    favourite_movies_series_others = models.TextField(blank=True)
    # que te gusta compartir o ensenyar
    what_you_like_sharing = models.TextField(blank=True)
    # cosas increibles que hayas hecho o visto
    incredible_done_seen = models.TextField(blank=True)
    # opinion sobre peoplewings
    pw_opinion = models.TextField(blank=True)
    political_opinion = models.CharField(max_length=20, blank=True)
    religion = models.CharField(max_length=20, blank=True)
    # citas
    quotes = models.TextField(blank=True)
    people_inspired_you = models.TextField(blank=True)
    places_lived_in = models.TextField(blank=True)
    places_wanna_go = models.TextField(blank=True)
    places_gonna_go = models.TextField(blank=True)
    relationships = models.ManyToManyField("self", symmetrical=False, through='Relationship')

"""
anyadir atributo through='Studies' al campo UserProfile.universities

class Studies(models.Model):
    degree = models.CharField(max_length=30)
    user_profile = models.ForeignKey('UserProfile')
    university = models.ForeignKey('University')
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

def createUserProfile(sender, user, request, **kwargs):
    form = RegistrationForm(request.POST)
    registered_user = User.objects.get(username=user.username)
    registered_user.last_name = kwargs['lastname']
    registered_user.first_name = kwargs['firstname']
    registered_user.save()
    data = UserProfile.objects.create(user=user)
    data.gender = form.data["gender"]
    data.birthday = datetime(year=int(form.data["birthday_year"]), month=int(form.data["birthday_month"]), day=int(form.data["birthday_day"]))
    """
    today = date.today()
    age = today.year - form.data["birthday"].year
    if today.month < form.data["birthday"].month or (today.month == form.data["birthday"].month and today.day < form.data["birthday"].day): age -= 1
    data.age = age
    """
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