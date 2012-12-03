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
        ('M', 'Maybe'),
    )

# Notifications class
class Notifications(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='%(class)s_receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, related_name='%(class)s_sender', on_delete=models.CASCADE)   
    created = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=36, blank=False)
    read = models.BooleanField(default=False)
    kind = models.CharField(max_length=15, null=True)

# Request class
class Requests(Notifications):    
    title = models.CharField(max_length = 100, blank=False)
    state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    public_message = models.TextField(blank=True)
    private_message = models.TextField(blank=True)
    make_public = models.BooleanField(default=False)
    wing = models.ForeignKey(Wing, related_name='%(class)s_wing', on_delete=models.CASCADE, null=False)

    def save(self):
        self.kind = 'requests'
        super(Requests, self).save()

# Invite class
class Invites(Notifications):
    title = models.CharField(max_length = 100, blank=False)
    state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    private_message = models.TextField(blank=True)
    wing = models.ForeignKey(Wing, related_name='%(class)s_wing', on_delete=models.CASCADE, null=False)

    def save(self):
        self.kind = 'invites'
        super(Invites, self).save()

# Messages class
class Messages(Notifications): 
    private_message = models.TextField(blank=True)

    def save(self):
        self.kind = 'messages'
        super(Messages, self).save()

# Friendship class
class Friendship(Notifications):
    message = models.TextField(blank=True)

    def save(self):
        self.kind = 'friendship'
        super(Friendship, self).save()

# AditionalInformation class
class AdditionalInformation(models.Model):
    notification = models.ForeignKey(Notifications, related_name = '%(class)s_notification', on_delete=models.CASCADE)
    modified = models.BooleanField(default=False)
    class Meta:
        abstract = True

# Accomodation class
class AccomodationInformation(AditionalInformation):
    start_date = models.DateField()
    end_date = models.DateField()
    transport = models.CharField(max_length = 50)
    num_people = models.IntegerField(default=1)

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


