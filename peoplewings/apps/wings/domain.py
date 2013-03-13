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

class AccomodationWingEditable(object):

	def __init__(self):
		self.id = None		
		self.name = None
		self.status = None
		self.date_start = None
		self.date_end = None
		self.best_days = None
		self.is_request = None
		self.city = {}
		self.active = None
		self.sharing_once = None
		self.capacity = None
		self.preferred_male = None
		self.preferred_female = None
		self.wheelchair = None
		self.where_sleeping_type = None
		self.smoking = None
		self.i_have_pet = None
		self.pets_allowed = None
		self.blankets = None
		self.live_center = None
		self.about = None
		self.address = None
		self.number = None
		self.additional_information = None
		self.postal_code = None

		self.bus = False
		self.train = False
		self.tram = False
		self.underground = False
		self.boat = False
		self.others = False

	def jsonable(self):
		res = dict()
		for key, value in self.__dict__.items():   
			if value is not None:         
				res[key] = value
		return res