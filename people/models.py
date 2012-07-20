from django.db import models
from django.contrib.auth.models import User
from registration.signals import user_activated
from django.utils import timezone
from datetime import date, datetime
from sets import Set

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
    interested_in = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    civil_state = models.CharField(max_length=2, choices=CIVIL_STATE_CHOICES, null=True)
    #languages = set(models.CharField(max_length=2, choices=LANGUAGES_CHOICES))
    languages = set()
    city = models.CharField(max_length=20)
    PW_state = models.CharField(max_length=1, choices=PW_STATE_CHOICES, null=True)
    privacy_settings = models.CharField(max_length=1, choices=PRIVACY_CHOICES, default='M')
    relationships = models.ManyToManyField("self", symmetrical=False, through='Relationship')


def createUserProfile(sender, user, request, **kwargs):
	UserProfile.objects.create(user=user)

user_activated.connect(createUserProfile)

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
