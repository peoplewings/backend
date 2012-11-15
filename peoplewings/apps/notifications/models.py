from django.db import models
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.wings.models import Wing
from django.db.models.signals import post_save, post_delete
from django.db.models import signals
import uuid

TYPE_CHOICES = (
        ('A', 'Accepted'),
        ('P', 'Pending'),
        ('D', 'Denyed'),
    )

# Notifications class
class Notifications(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='%(class)s_receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, related_name='%(class)s_sender', on_delete=models.CASCADE)
    title = models.CharField(max_length = 100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=36, blank=False)

# Request class
class Requests(Notifications):    
    num_people = models.IntegerField(default=1)
    read = models.BooleanField(default=False)   
    state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    public_message = models.TextField(blank=True)
    private_message = models.TextField(blank=True)
    make_public = models.BooleanField(default=False)
    wing = models.ForeignKey(Wing, related_name='%(class)s_wing', on_delete=models.CASCADE, null=False)

# Invite class
class Invites(Notifications):
    num_people = models.IntegerField(default=1)
    read = models.BooleanField(default=False)    
    state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    private_message = models.TextField(blank=True)
    wing = models.ForeignKey(Wing, related_name='%(class)s_wing', on_delete=models.CASCADE, null=False)

# Messages class
class Messages(Notifications): 
    private_message = models.TextField(blank=True)
    read = models.BooleanField(default=False)

# AditionalInformation class
class AditionalInformation(models.Model):
    notification = models.ForeignKey(Notifications, related_name = '%(class)s_notification', on_delete=models.CASCADE)
    class Meta:
        abstract = True

# Accomodation class
class AccomodationInformation(AditionalInformation):
    title = models.CharField(max_length = 100, blank=False)
    start_date = models.DateField()
    end_date = models.DateField()
    transport = models.CharField(max_length = 50)

# NotificationsAlarm class
# This class will be used as a fast access class to see if user has new notifications
class NotificationsAlarm(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='alarm_receiver', on_delete=models.CASCADE)
    notificated = models.BooleanField(default=False)
    reference = models.CharField(max_length=36, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True)

def put_alarm(sender, instance, signal, *args, **kwargs):
    notif = NotificationsAlarm()
    notif.receiver = instance.receiver
    notif.notificated = False
    notif.reference = instance.reference

def del_alarm(sender, instance, signal, *args, **kwargs):
    try:
        notifa = NotificationsAlarm.objects.get(reference = instance.reference)
        notifa.delete()
    except MultipleObjectsReturned:
        pass

post_save.connect(put_alarm, sender=Notifications)
post_delete.connect(del_alarm, sender=Notifications)


