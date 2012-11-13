from django.db import models
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.wings.models import Wing
import uuid
from django.db.models.signals import post_save
from django.db.models import signals

TYPE_CHOICES = (
        ('A', 'Accepted'),
        ('P', 'Pending'),
        ('D', 'Denyed'),
    )

# NotificationsAlarm class
# This class will be used as a fast access class to see if user has new notifications
class NotificationsAlarm(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='receiver', on_delete=models.CASCADE)
    notificated = models.BooleanField(default=False)
    reference = models.ForeignKey(Notifications, related_name='notification', on_delete=models.CASCADE)

# Notifications class
class Notifications(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, related_name='sender', on_delete=models.CASCADE)
    title = models.CharField(max_length = 100, blank=False)
    created = models.DateField(auto_now_add=True)
    reference = models.CharField(max_length=36, blank=False)

# Request class
class Requests(Notifications):    
    num_people = models.IntegerField(default=1)
    read = models.BooleanField(default=False)   
    state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    public_message = models.TextField(blank=True)
    private_message = models.TextField(blank=True)
    make_public = models.BooleanField(default=False)
    wing_id = models.ForeignKey(Wing, related_name='wing', on_delete=models.CASCADE, null=False)

# Invite class
class Invites(Notifications):
    num_people = models.IntegerField(default=1)
    read = models.BooleanField(default=False)    
    state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    private_message = models.TextField(blank=True)
    wing_id = models.ForeignKey(Wing, related_name='wing', on_delete=models.CASCADE, null=False)

# Messages class
class Messages(Notifications): 
    reference = models.CharField(max_length=36, blank=False)
    private_message = models.TextField(blank=True)
    read = models.BooleanField(default=False)

# AditionalInformation class
class AditionalInformation(models.Model):
    notification = models.ForeignKey(Notifications, related_name = '%(class)s', on_delete=models.CASCADE)
    class Meta:
        abstract = True

# Accomodation class
class Accomodation(AditionalInformation):
    title = models.CharField(max_length = 100, blank=False)
    start_date = models.DateField()
    end_date = models.DateField()
    transport = models.CharField(max_length = 50)

def put_alarm(sender, instance, signal, *args, **kwargs):
    notif = NotificationsAlarm()
    notif.receiver = instance.id_receiver
    notif.notificated = False
    notif.reference = instance.reference

def del_alarm(sender, instance, signal, *args, **kwargs):
    try:
        notifa = NotificationsAlarm.objects.get(reference = instance.reference)
        notifa.delete()
    except MultipleObjectsReturned:

post_save.connect(put_alarm, sender=Notifications)
post_delete.connect(del_alarm, sender=Notifications)


