from django.db import models
import json

class ShortWings(object):
	
	def __init__(self):
		self.idWing = None
		self.wingName = None
		self.wingType = None

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res

class WingObj(object):
	def __init__(self):
		self.idWing=None
		self.author = None
		self.name=None
		self.status=None
		self.type=None
		self.dateStart=None
		self.dateEnd=None
		self.bestDays=None
		self.city=None
		self.extraFields={}

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res