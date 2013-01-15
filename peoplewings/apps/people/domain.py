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