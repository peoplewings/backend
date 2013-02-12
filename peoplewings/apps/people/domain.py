from django.db import models
from django.conf import settings
import json
from notifications.models import Notifications
from django.db.models import Q

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
		self._online = None

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

	def score_experience(self, data):
		photo_score = getattr(settings, 'PHOTO_SCORE', 0)
		max_photos = getattr(settings, 'MAX_UPLOADED_PHOTOS', 0)
		for i in data:
			#To be done
			i['_experience_score'] = 0
		return data

	def score_responsive(self, data):
		rr_100 = getattr(settings, 'REPLY_RATE_100', 0)
		rr_90 = getattr(settings, 'REPLY_RATE_90', 0)
		rr_80 = getattr(settings, 'REPLY_RATE_80', 0)
		rr_70 = getattr(settings, 'REPLY_RATE_70', 0)
		rr_60 = getattr(settings, 'REPLY_RATE_60', 0)
		rr_50 = getattr(settings, 'REPLY_RATE_50', 0)
		rr_sub50 = getattr(settings, 'REPLY_RATE_sub50', 0)

		rt_1 = getattr(settings, 'REPLY_TIME_1H', 0)
		rt_4 = getattr(settings, 'REPLY_TIME_4H', 0)
		rt_12 = getattr(settings, 'REPLY_TIME_12H', 0)
		rt_24 = getattr(settings, 'REPLY_TIME_24H', 0)
		rt_48 = getattr(settings, 'REPLY_TIME_48H', 0)
		rt_1w = getattr(settings, 'REPLY_TIME_1W', 0)
		rt_super1w = getattr(settings, 'REPLY_TIME_super1W', 0)

		for i in data:
			score = 0
			if self.reply_rate == 100: score = rr_100
			elif self.reply_rate >= 90: score = rr_90
			elif self.reply_rate >= 80: score = rr_80
			elif self.reply_rate >= 70: score = rr_70
			elif self.reply_rate >= 60: score = rr_60
			elif self.reply_rate >= 50: score = rr_50
			else: score = rr_sub50

			if self.reply_time <= 3600: score = score + rt_1
			elif self.reply_time <= 3600 * 4: score = score + rt_4
			elif self.reply_time <= 3600 * 12: score = score + rt_12
			elif self.reply_time <= 3600 * 24: score = score + rt_24
			elif self.reply_time <= 3600 * 48: score = score + rt_48
			elif self.reply_time <= 3600 * 24 * 7: score = score + rt_1w
			else: score = score + rt_super1w
			i['_responsive_score'] = score
		return data

	def score_reqinv(self, data):
		pop_24_0 = getattr(settings, 'POPULARITY_24H_0', 0)
		pop_24_1 = getattr(settings, 'POPULARITY_24H_1', 0)
		pop_24_5 = getattr(settings, 'POPULARITY_24H_5', 0)
		pop_24_10 = getattr(settings, 'POPULARITY_24H_10', 0)
		pop_24_15 = getattr(settings, 'POPULARITY_24H_15', 0)
		pop_24_20 = getattr(settings, 'POPULARITY_24H_20', 0)
		pop_24_super20 = getattr(settings, 'POPULARITY_24H_super20', 0)

		pop_1w_0 = getattr(settings, 'POPULARITY_1W_0', 0)
		pop_1w_5 = getattr(settings, 'POPULARITY_1W_5', 0)
		pop_1w_10 = getattr(settings, 'POPULARITY_1W_10', 0)
		pop_1w_15 = getattr(settings, 'POPULARITY_1W_15', 0)
		pop_1w_20 = getattr(settings, 'POPULARITY_1W_20', 0)
		pop_1w_25 = getattr(settings, 'POPULARITY_1W_25', 0)
		pop_1w_30 = getattr(settings, 'POPULARITY_1W_30', 0)
		pop_1w_50 = getattr(settings, 'POPULARITY_1W_50', 0)
		pop_1w_70 = getattr(settings, 'POPULARITY_1W_70', 0)

		for i in data:
			score = 0
			n24 = 0
			prof = UserProfile.objects.get(pk=i.profile_id)
			notifs = Request.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24)))
			for n in notifs:
				if n.state == 'P':
					n24 = n24 + 1
			notifs = Invites.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24)))
			for n in notifs:
				if n.state == 'P':
					n24 = n24 + 1
			n1w = 0
			notifs = Request.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24*7)))
			for n in notifs:
				if n.state == 'P':
					n1w = n1w + 1
			notifs = Invites.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24*7)))
			for n in notifs:
				if n.state == 'P':
					n1w = n1w + 1

			if n24 == 0: score = pop_24_0
			elif n24 < 5: score = pop_24_1
			elif n24 < 10: score = pop_24_5
			elif n24 < 15: score = pop_24_10
			elif n24 < 20: score = pop_24_15
			elif n24 == 20: score = pop_24_20
			else: score = pop_24_super20

			if n1w == 0: score = score + pop_1w_0
			elif n1w < 5: score = score + pop_1w_1
			elif n1w < 10: score = score + pop_1w_5
			elif n1w < 15: score = score + pop_1w_10
			elif n1w < 20: score = score + pop_1w_15
			elif n1w < 25: score = score + pop_1w_20
			elif n1w < 30: score = score + pop_1w_25
			elif n1w < 50: score = score + pop_1w_30
			elif n1w < 70: score = score + pop_1w_50
			else: score = score + pop_1w_70

			i['_reqinv_score'] = score
		return data

	def sum_score(self, obj):
		obj['final_score'] = obj['_reqinv_score'] + obj['_responsive_score'] + obj['_experience_score']
		return obj

	def order_by_relevance_score(self, data):
		data = self.score_experience(data)
		data = self.score_responsive(data)
		data = self.score_reqinv(data)
		data = [self.sum_score(i) for i in data]
		return sorted(data, key=attrgetter('final_score'), reverse=True)

	def order_by_relevance_plus_news(self, data):
		old = list(data)
		new = list(data)
		final = []
		old = sorted(old, key=attrgetter('date_joined'), reverse=False)
		new = sorted(new, key=attrgetter('date_joined'), reverse=True)

		old = self.order_by_relevance_score(old)

		idx_old = 0
		idx_new = 0
		length = len(old)
		switch = True

		while idx_old < length and idx_new < length:
			while idx_old < length and switch == True:
				#Add an OLD
				if old[idx_old] not in final:
					final.append(old[idx_old])
					switch = False
				else:
					idx_old = idx_old + 1
			while idx_new < length and switch == False:
				#Add an NEW
				if new[idx_new] not in final:
					final.append(new[idx_new])
					switch = True
				else:
					idx_new = idx_new + 1
		while idx_old < length:
			if old[idx_old] not in final:
				final.append(old[idx_old])

		while idx_new < length:
			if new[idx_new] not in final:
				final.append(new[idx_new])
		return final

	def order_by_relevance(self):
		#Split onlines and offlines
		online = [i for i in self.objects if i._online == True]
		offline = [i for i in self.objects if i._online == False]

		online = self.order_by_relevance_plus_news(online)
		offline = self.order_by_relevance_plus_news(offline)

		return online + offline

