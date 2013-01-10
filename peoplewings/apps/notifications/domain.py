from django.db import models
import json
from peoplewings.apps.notifications.models import USERSTATE_CHOICES, TYPE_CHOICES

class NotificationsList(object):
	## Notif specific
	def __init__(self):
		self.id = None
		self.created = None
		self.read = None
		self.kind = None
		self.reference = None
		## Request/inv specific
		self.state = None
		self.flag_direction = None
		self.start_date = None
		self.end_date = None
		self.num_people = None
		self.message = None
		self.wing_type =  None
		## Msg/req/inv specific
		self.content = None
		#Profile specific
		self.interlocutor_id = None
		self.name = None
		self.avatar =  None
		self.age = None
		self.verified = None
		self.location = None
		self.connected = None
		## URLs
		self.thread_url = None

	def gen_key(self, key):
		buff = key.replace("_", " ")
		buff = buff.split()
		buff = [i.capitalize() for i in buff if len(buff) > 1]
		buff = "".join(buff)
		return buff

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res

	def search(self, key):
		if (self.name is not None and key.lower() in self.name.lower()) or (self.message is not None and key.lower() in self.message.lower()) or (self.content is not None and key.lower() in self.content.lower()):
			return True
		return False

class MessageThread(object):
	## Notif specific
	def __init__(self):
		#sender info
		self.sender_id = None
		self.sender_name = None
		self.sender_age = None
		self.sender_verified = None
		self.sender_location = None
		self.sender_friends = None
		self.sender_references = None
		self.sender_med_avatar = None
		self.sender_small_avatar = None
		self.sender_connected = None
		#receiver info
		self.receiver_id = None
		self.receiver_avatar = None
		#message info
		self.content = {}
		self.content['message'] = None
		#generic info
		self.kind = None
		self.created = None
		self.reference = None
		self.id = None
	
	def gen_key(self, key):
		buff = key.replace("_", " ")
		buff = buff.split()
		buff = [i.capitalize() for i in buff if len(buff) > 1]
		buff = "".join(buff)
		return buff

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res


class Thread(object):
	#Thread specific
	id = models.IntegerField()
	created = models.BigIntegerField()
	read = models.BooleanField()
	kind = models.CharField()
	#Profile specific
	interlocutor_id = models.CharField()
	name = models.CharField()
	med_avatar =  models.CharField()
	small_avatar = models.CharField()
	age = models.IntegerField()
	verified = models.BooleanField()
	location = models.TextField()
	connected = models.CharField(choices = USERSTATE_CHOICES, default = 'F')
	friends = models.IntegerField()
	references = models.IntegerField()
	#Req/invite specific


class AccomodationRequestThread(object):
	## Notif specific
	id  = models.IntegerField()
	sender = models.IntegerField()
	receiver = models.IntegerField()
	created = models.CharField()
	reference = models.CharField()
	read = models.BooleanField()
	kind = models.CharField()
	## AccomodationRequest specific
	wing_name = models.CharField()
	wing_id = models.CharField()
	state = models.CharField()        
	start_date = models.DateField()
	end_date = models.DateField()
	num_people = models.IntegerField()
	transport = models.CharField()
	private_message = models.TextField()
	#Sender specific
	nameS = models.CharField()    
	ageS = models.IntegerField()
	verifiedS = models.BooleanField()
	locationS = models.TextField()
	friendsS = models.IntegerField()
	referencesS = models.IntegerField()
	med_avatarS =  models.CharField()
	small_avatarS = models.CharField()
	#Receiver specific
	nameR = models.CharField()    
	ageR = models.IntegerField()
	verifiedR = models.BooleanField()
	locationR = models.TextField()
	friendsR = models.IntegerField()
	referencesR = models.IntegerField()
	med_avatarR =  models.CharField()
	small_avatarR = models.CharField()

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():            
			res[key] = value
		return res

def ComplexHandler(Obj):
	if hasattr(Obj, 'jsonable'):
		return Obj.jsonable()
	else:
		return json.JSONEncoder.default(self, obj)
	
