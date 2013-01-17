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
		self.created = None		
	
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

class RequestItem(object):
	def __init__(self):
		#sender info
		self.senderId= None
		self.senderName= None
		self.senderAge= None
		self.senderVerified= None
		self.senderLocation= None	             
		self.senderFriends= None
		self.senderReferences= None
		self.senderMedAvatar= None
		self.senderSmallAvatar= None
		self.senderConnected= None
		self.content= {}
		self.content['message']= None
		self.receiverId= None
		self.receiverAvatar= None
		self.created= None

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res

class RequestThread(object):
	def __init__(self):
		#sender info
		self.reference= None
		self.kind= None
		self.firstSender= None
		self.wing= {}
		self.wing['type'] = None
		self.wing['state'] = None
		self.wing['parameters'] = {}
		self.wing['parameters']['wingId']= 34
		self.wing['parameters']['wingName']= None
		self.wing['parameters']['wingCity']= None
		self.wing['parameters']['startDate']= None
		self.wing['parameters']['endDate']= None
		self.wing['parameters']['capacity']= None
		self.wing['parameters']['arrivingVia']= None
		self.wing['parameters']['flexibleStartDate']= None
		self.wing['parameters']['flexibleEndDate']= None
		self.options= {}
		self.options['canAccept']= None
		self.options['canMaybe']= None
		self.options['canPending']= None
		self.options['canDeny']= None
		self.items = []

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res

def ComplexHandler(Obj):
	if hasattr(Obj, 'jsonable'):
		return Obj.jsonable()
	else:
		return json.JSONEncoder.default(self, obj)
	
