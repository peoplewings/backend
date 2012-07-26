from django.db import models
from django.contrib.auth.models import User
from registration.signals import user_registered
from people.signals import *
from django.utils import timezone
from datetime import date, datetime
from registration.forms import RegistrationForm
from sets import Set

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
    
    LANGUAGES_CHOICES = (
        ('EN', 'English'),
        ('SP', 'Spanish'),
        ('FR', 'French'),
        ('IT', 'Italian'),
        ('GE', 'German'),
        ('CH', 'Chinese'),
        ('JA', 'Japanese'),
        ('AR', 'Arab'),
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
    birthday = models.DateField(null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    interested_in = models.CharField(max_length=1, choices=INTERESTED_IN_GENDER_CHOICES, null=True)
    civil_state = models.CharField(max_length=2, choices=CIVIL_STATE_CHOICES, null=True)
    #languages = set(models.CharField(max_length=2, choices=LANGUAGES_CHOICES))
    languages = set()
    city = models.CharField(max_length=20)
    pw_state = models.CharField(max_length=1, choices=PW_STATE_CHOICES, null=True)
    #privacy_settings = models.CharField(max_length=1, choices=PRIVACY_CHOICES, default='M')
    all_about_you = models.TextField(default='')
    main_mission = models.TextField(default='')
    occupation = models.CharField(max_length=20, default='')
    education = models.CharField(max_length=20, default='')
    # experiencia sobre pw
    pw_experience = models.TextField(default='')
    personal_philosophy = models.TextField(default='')
    other_pages_you_like = models.TextField(default='')
    people_you_like = models.TextField(default='')
    # peliculas, libros, series, videojuegos, music, deportes, actividades favoritas
    favourite_movies_series_others = models.TextField(default='')
    # que te gusta compartir o ensenyar
    what_you_like_sharing = models.TextField(default='')
    # cosas increibles que hayas hecho o visto
    incredible_done_seen = models.TextField(default='')
    # opinion sobre peoplewings
    pw_opinion = models.TextField(default='')
    political_opinion = models.CharField(max_length=20, default='')
    religion = models.CharField(max_length=20, default='')
    # citas
    quotes = models.TextField(default='')
    people_inspired_you = models.TextField(default='')
    relationships = models.ManyToManyField("self", symmetrical=False, through='Relationship')

class Relationship(models.Model):

    RELATIONSHIP_CHOICES = (
        ('F', 'Friend'),
        ('P', 'Pendent'),
        ('B', 'Blocked'),
        ('R', 'Rejected'),
    )
    type = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES, null=True)
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
	data.birthday = form.data["birthday"]
	data.save()

def deleteUserProfile(sender, request, **kwargs):
    prof = request.user.get_profile()
    prof.delete()

user_registered.connect(createUserProfile)
user_deleted.connect(deleteUserProfile)