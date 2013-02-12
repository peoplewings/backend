from django.db import models
from django.db.models import Q
import json


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
		## Msg specific
		self.content = None
		#Profile specific
		self.interlocutor_id = None
		self.name = None
		self.avatar =  None
		self.age = None
		self.verified = None
		self.location = None
		self.online = None
		#Wing Params
		self.wing_parameters = {}
		self.wing_parameters['start_date'] = None
		self.wing_parameters['end_date'] = None
		self.wing_parameters['num_people'] = None
		self.wing_parameters['message'] = None
		self.wing_parameters['wing_type'] = None
		self.wing_parameters['wing_city'] = None
		self.wing_parameters['modified'] = None

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

		if (self.name is not None and key.lower() in self.name.lower()):
			return True
		if (self.age is not None and key == self.age):
			return True
		if (self.location is not None and key.lower in self.location.lower()):
			return True
		if (self.content is not None and key.lower in self.content.lower()):
			return True
		if (self.wing_parameters['start_date'] is not None and key in self.wing_parameters['start_date']):
			return True
		if (self.wing_parameters['end_date'] is not None and key in self.wing_parameters['end_date']):
			return True
		if (self.wing_parameters['wing_type'] is not None and key.lower() in self.wing_parameters['wing_type'].lower()):
			return True
		if (self.wing_parameters['wing_city'] is not None and key.lower() in self.wing_parameters['wing_city'].lower()):
			return True
		if (self.wing_parameters['message'] is not None and key.lower() in self.wing_parameters['message'].lower()):
			return True
		if (self.id is not None and self.kind is not None and self.kind == 'request' or self.kind == 'invite'):
			filters_req = Q(pk=self.id)&(Q(private_message__icontaints=key)|Q(public_message__icontaints=key))
			filters_inv = Q(pk=self.id)&Q(private_message__icontaints=key)
			if self.kind == 'request' and len(Requests.objects.filter(filters_req)) > 0:
				return True
			elif self.kind == 'invite' and len(Invites.objects.filter(filters_inv)) > 0:
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
		self.sender_online = None
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
		self.senderOnline= None
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
		self.wing['parameters']['modified']= None
		self.options = []
		self.items = []

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res

class Automata(object):

	def check_P(self, stats, me):
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'P':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'P':
					return self.check_P(stats, me)
				elif next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
			else:
				if next[0] == 'A':
					result = self.check_PTA(stats, me)
					return result
				elif next[0] == 'M':
					return self.check_PTM(stats, me)
				elif next[0] == 'D':
					return self.check_PTD(stats, me)
				else:
					return False
		else: 
			return False

	def check_PYD(self, stats, me):
		
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'D':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'P':
					return self.check_P(stats, me)
				elif next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
			else:
				if next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
		else:
			return False

	def check_PTA(self, stats, me):
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'A':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'A':
					return self.check_PTA(stats, me)
				elif next[0] == 'M':
					return self.check_PTAYM(stats, me)
				elif next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
			else:
				if next[0] == 'A':
					return self.check_PTA(stats, me)
				elif next[0] == 'M':
					return self.check_PTM(stats, me)
				elif next[0] == 'D':
					return self.check_PTD(stats, me)
				else:
					return False
		else:
			return False

	def check_PTM(self, stats, me):
		
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'M':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'M':
					return self.check_PTM(stats, me)###!!!!
				elif next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
			else:
				if next[0] == 'A':
					return self.check_PTA(stats, me)
				elif next[0] == 'M':
					return self.check_PTM(stats, me)
				elif next[0] == 'D':
					return self.check_PTD(stats, me)
				else:
					return False
		else:
			return False

	def check_PTAYM(self, stats, me):
		
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'M':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'A':
					return self.check_PTA(stats, me)
				elif next[0] == 'M':
					return self.check_PTAYM(stats, me)
				elif next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
			else:
				if next[0] == 'M':
					return self.check_PTAYM(stats, me)
				elif next[0] == 'D':
					return self.check_PTAYMTD(stats, me)
				else:
					return False
		else:
			return False

	def check_PTAYMTD(self, stats, me):
		
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'D':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'D':
					return self.check_PTAYMTD(stats, me)
				else:
					return False
			else:
				if next[0] == 'D':
					return self.check_PTAYMTD(stats, me)
				elif next[0] == 'M':
					return self.check_PTAYMTDTM(stats, me)
				else:
					return False
		else:
			return False

	def check_PTAYMTDTM(self, stats, me):
		
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'M':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'A':
					return self.check_PTA(stats, me)
				elif next[0] == 'M':
					return self.check_PTAYMTDTM(stats, me)
				elif next[0] == 'D':
					return self.check_PYD(stats, me)
				else:
					return False
			else:
				if next[0] == 'M':
					return self.check_PTAYMTDTM(stats, me)
				elif next[0] == 'D':
					return self.check_PTAYMTD(stats, me)
				else:
					return False
		else:
			return False

	def check_PTD(self, stats, me):
		
		current = stats.pop(0)
		if len(stats) == 0:
			return True
		if current[0] == 'D':
			next = stats[0]
			if next[1] == me.pk:
				if next[0] == 'D':
					return self.check_PTD(stats, me)
				else:
					return False
			else:
				if next[0] == 'D':
					return self.check_PTD(stats, me)
				elif next[0] == 'M':
					return self.check_PTM(stats, me)
				elif next[0] == 'A':
					return self.check_PTA(stats, me)
				else:
					return False
		else:
			return False




def ComplexHandler(Obj):
	if hasattr(Obj, 'jsonable'):
		return Obj.jsonable()
	else:
		return json.JSONEncoder.default(self, obj)
	
