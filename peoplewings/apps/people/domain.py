from django.db import models
import json

class Contacts(object):
	
	def __init__(self):
		self.id = None
		self.name = None
		self.lastName = None

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res

class SearchObject(object):
	def __init__(self):
		self.profile_id = None
		self.first_name = None
		self.last_name = None
		self.current = None
		self.avatar = None
		self.age = None
		self.online = None
		self.reply_rate = None
		self.reply_time = None
		self.languages = None
		self.all_about_you = None
		self.date_joined = None

		self._user = None

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None and not key.startswith('_'):       
				res[key] = value
		return res
		
class SearchObjectManager(object):
	def __init__(self):
		self.objects = []

	def jsonable_item(self, obj):
		res = dict()
		for key, value in obj.__dict__.items():   
			if value is not None and not key.startswith('_'):         
				res[key] = value
		return res

	def jsonable(self):
		res = []
		for i in self.objects:
			res.append(self.jsonable_item(i))
		return res