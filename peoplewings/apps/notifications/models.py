from django.db import models
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.wings.models import Wing
from django.db.models.signals import post_save, post_delete
from django.db.models import signals
from django.db.models import Q
import uuid
import time
import copy

TYPE_CHOICES = (
		('A', 'Accepted'),
		('P', 'Pending'),
		('D', 'Denyed'),
		('M', 'Maybe'),
	)

USERSTATE_CHOICES = (
		('O', 'Online'),
		('F', 'Offline'),
	)

class NotificationsManager(models.Manager):
	def create_message(self, **kwargs):
		try:
			rec = UserProfile.objects.get(pk = kwargs['receiver'])
		except Exception, e:
			raise e
		try:
			sen = UserProfile.objects.get(user = kwargs['sender'])
		except Exception, e:
			raise e			
		notif = Messages.objects.create(receiver = rec, sender = sen, created = time.time(), reference = uuid.uuid4(), kind = 'message', read = False, first_sender =  sen, private_message = kwargs['content'])

	def respond_message(self, **kwargs):
		try:
			rec = UserProfile.objects.get(pk = kwargs['receiver'])
		except Exception, e:
			raise e
		try:
			sen = UserProfile.objects.get(user = kwargs['sender'])
		except Exception, e:
			raise e
		try:			
			fs = Notifications.objects.filter(reference= kwargs['reference']).order_by('created')[0]
		except Exception, e:
			raise e
		notif = Messages.objects.create(receiver = rec, sender = sen, created = time.time(), reference = kwargs['reference'], kind = 'message', read = False, first_sender =  fs.first_sender, private_message = kwargs['content'])
		thread = Notifications.objects.filter(reference = kwargs['reference'])
		for i in thread:
			i.first_sender_visible = True
			i.second_sender_visible = True
			i.save()

	def respond_request(self, **kwargs):		
		reference = kwargs['reference']
		receiver_id = kwargs['receiver']
		sender_id = kwargs['sender']
		content = kwargs['content'] 
		state = kwargs['state']
		receiver = UserProfile.objects.get(pk=receiver_id)
		sender = UserProfile.objects.get(pk=sender_id)
		thread = Requests.objects.filter(reference= reference).order_by('created')
		thread_len = len(thread)
		last_state = thread[thread_len-1].state
		first_sender = thread[0].first_sender
		wing = thread[0].wing

		created = time.time()
		notif = Requests.objects.create(receiver= receiver, sender= sender, created = created, reference = reference, kind = 'request', read = False, first_sender =  first_sender, private_message = content, public_message = "", state = state, wing=wing)
		thread = Notifications.objects.filter(reference = kwargs['reference'])
		for i in thread:
			i.first_sender_visible = True
			i.second_sender_visible = True
			i.save()
		return notif

	def respond_invite(self, **kwargs):		
		reference = kwargs['reference']
		receiver_id = kwargs['receiver']
		sender_id = kwargs['sender']
		content = kwargs['content'] 
		state = kwargs['state']
		receiver = UserProfile.objects.get(pk=receiver_id)
		sender = UserProfile.objects.get(pk=sender_id)
		thread = Invites.objects.filter(reference= reference)		
		thread_len = len(thread)
		last_state = thread[thread_len-1].state
		first_sender = thread[0].first_sender
		wing = thread[0].wing

		created = time.time()
		notif = Invites.objects.create(receiver= receiver, sender= sender, created = created, reference = reference, kind = 'invite', read = False, first_sender =  first_sender, private_message = content, state = state, wing=wing)
		thread = Notifications.objects.filter(reference = kwargs['reference'])
		for i in thread:
			i.first_sender_visible = True
			i.second_sender_visible = True
			i.save()
		return notif

	def create_request(self, **kwargs):
		try:
			receiver = UserProfile.objects.get(pk = kwargs['receiver'])
		except Exception, e:
			raise e
		try:
			sender = UserProfile.objects.get(user = kwargs['sender'])
		except Exception, e:
			raise e
		try:
			wing = Wing.objects.get(pk= kwargs['wing'])
		except Exception, e:
			raise e
		notif = Requests.objects.create(receiver = receiver, sender = sender, created = time.time(), reference = uuid.uuid4(), kind = 'request', read = False, 
						first_sender =  sender, private_message = kwargs['private_message'], public_message = kwargs['public_message'], 
						state = 'P', make_public = kwargs['make_public'], wing = wing)
		return notif

	def create_invite(self, **kwargs):
		try:
			receiver = UserProfile.objects.get(pk = kwargs['receiver'])
		except Exception, e:
			raise e
		try:
			sender = UserProfile.objects.get(user = kwargs['sender'])
		except Exception, e:
			raise e
		try:
			wing = Wing.objects.get(pk= kwargs['wing'])
		except Exception, e:
			raise e
		notif = Invites.objects.create(receiver = receiver, sender = sender, created = time.time(), reference = uuid.uuid4(), kind = 'invite', read = False, 
						first_sender =  sender, private_message = kwargs['private_message'], state = 'P',  wing = wing)
		return notif

	def invisible_notification(self, ref, user):
		try:
			notif = self.filter(reference = ref)
			for i in notif:
				if (i.first_sender == user):
					i.first_sender_visible = False
				else:
					i.second_sender_visible = False
				try:
					alarms = NotificationsAlarm.objects.filter(receiver = user, reference=ref)
					for a in alarms:
						a.delete()
				except:
					pass
				i.save()
		except:
			pass

# Notifications class
class Notifications(models.Model):
	objects = NotificationsManager()
	receiver = models.ForeignKey(UserProfile, related_name='%(class)s_receiver', on_delete=models.CASCADE)
	sender = models.ForeignKey(UserProfile, related_name='%(class)s_sender', on_delete=models.CASCADE)   
	created = models.BigIntegerField(default=0)
	reference = models.CharField(max_length=36, blank=False)
	read = models.BooleanField(default=False)
	kind = models.CharField(max_length=15, null=True)
	first_sender = models.ForeignKey(UserProfile, related_name='%(class)s_first_sender', on_delete=models.CASCADE, null = True)
	first_sender_visible = models.BooleanField(default=True)
	second_sender_visible = models.BooleanField(default=True)

	def get_subclass(self):
		try:
			self.accomodationinformation_notification
			return self.accomodationinformation_notification
		except:
			pass
		return None
				
# Request class
class Requests(Notifications):
	state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
	public_message = models.TextField(blank=True)
	private_message = models.TextField(blank=True)
	make_public = models.BooleanField(default=False)
	wing = models.ForeignKey(Wing, related_name='%(class)s_wing', on_delete=models.CASCADE, null=False)

	def save(self, *args, **kwargs):
		self.kind = 'request'
		super(Requests, self).save(*args, **kwargs)

# Invite class
class Invites(Notifications):
	state = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
	private_message = models.TextField(blank=True)
	wing = models.ForeignKey(Wing, related_name='%(class)s_wing', on_delete=models.CASCADE, null=False)

	def save(self, *args, **kwargs):
		self.kind = 'invite'
		super(Invites, self).save(*args, **kwargs)

# Messages class
class Messages(Notifications): 
	private_message = models.TextField(blank=True)

	def save(self, *args, **kwargs):
		self.kind = 'message'
		super(Messages, self).save(*args, **kwargs)

# Friendship class
class Friendship(Notifications):
	message = models.TextField(blank=True)

	def save(self, *args, **kwargs):
		self.kind = 'friendship'
		super(Friendship, self).save(*args, **kwargs)

# AdditionalInformation class
class AdditionalInformation(models.Model):
	notification = models.ForeignKey(Notifications, related_name = '%(class)s_notification', on_delete=models.CASCADE)
	modified = models.BooleanField(default=False)
	class Meta:
		abstract = True        

#Accomodation info Manager
class AccomodationInformationManager(models.Manager):
	def get_or_none(self, **kwargs):
		try:
			return self.get(**kwargs)
		except self.model.DoesNotExist:
			return None

	def create_request(self, **kwargs):
		self.create(notification = kwargs['notification'], start_date =  kwargs['start_date'], end_date =  kwargs['end_date'], transport =  kwargs['transport'], num_people =  kwargs['num_people'], flexible_start = kwargs['flexible_start'], flexible_end =  kwargs['flexible_end'])

	def create_invite(self, **kwargs):
		self.create(notification = kwargs['notification'], start_date =  kwargs['start_date'], end_date =  kwargs['end_date'], num_people =  kwargs['num_people'], flexible_start = kwargs['flexible_start'], flexible_end =  kwargs['flexible_end'])

# Accomodation class
class AccomodationInformation(AdditionalInformation):
	objects = AccomodationInformationManager()
	start_date = models.BigIntegerField(default=0)
	end_date = models.BigIntegerField(default=0)
	transport = models.CharField(max_length = 50)
	num_people = models.IntegerField(default=1)
	flexible_start = models.BooleanField(default = False)
	flexible_end = models.BooleanField(default = False)
	def get_class_name(self):
		return 'accomodation'

# NotificationsAlarm class
# This class will be used as a fast access class to see if user has new notifications
class NotificationsAlarm(models.Model):
	receiver = models.ForeignKey(UserProfile, related_name='alarm_receiver', on_delete=models.CASCADE)
	notificated = models.BooleanField(default=False)
	reference = models.CharField(max_length=36, blank=False)
	created = models.BigIntegerField(default=0)

def put_alarm(sender, instance, signal, *args, **kwargs):
	notif = NotificationsAlarm()
	notif_aux= Notifications.objects.get(pk=instance.notifications_ptr.pk)
	filters = Q(reference= notif_aux.reference)&Q(receiver=notif_aux.receiver)
	if NotificationsAlarm.objects.filter(filters).count() == 0:
		notif.receiver = notif_aux.receiver
		notif.notificated = False
		notif.reference = notif_aux.reference
		notif.created = time.time()
		notif.save()
def del_alarm(sender, instance, signal, *args, **kwargs):
	filters = Q(reference= instance.reference)&Q(receiver=instance.receiver)
	NotificationsAlarm.objects.filter(filters).delete()


post_save.connect(put_alarm, sender=Messages)
post_save.connect(put_alarm, sender=Requests)
post_save.connect(put_alarm, sender=Invites)
#post_delete.connect(del_alarm, sender=Notifications)


