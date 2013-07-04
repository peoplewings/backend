from django.db import models
from django.conf import settings
import json
from notifications.models import Notifications
from django.db.models import Q
from people.models import UserProfile
from django.contrib.auth.models import User
from notifications.models import Requests, Invites
import time
from datetime import datetime, timedelta
from django.utils.timezone import utc

from operator import attrgetter

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
		self.wings = []

		self.wing_introduction = None
		self.wing_type = None
		self.wing_city = None
		self.wing_start_date = None
		self.wing_end_date = None
		self.wing_capacity = None

		self.ctrl_user = None
		self.ctrl_online = None

		self._experience_score= None
		self._responsive_score= None
		self._reqinv_score= None
		self._final_score= 0

		self.n_photos = None
		self._photos = None
		self._prof_complete = None
		self._recent = None


	def jsonable(self):
		res = dict()			
		for key, value in self.__dict__.items():   
			if value is not None and not key.startswith('ctrl_'):       
				res[key] = value
		return res
		
class SearchObjectManager(object):
	def __init__(self):
		self.objects = []

	def jsonable_item(self, obj):
		res = dict()
		for key, value in obj.__dict__.items():
			if value is not None and not key.startswith('ctrl_'):         
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
			i._experience_score = 0
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
			if i.reply_rate == 100: score = rr_100
			elif i.reply_rate >= 90: score = rr_90
			elif i.reply_rate >= 80: score = rr_80
			elif i.reply_rate >= 70: score = rr_70
			elif i.reply_rate >= 60: score = rr_60
			elif i.reply_rate >= 50: score = rr_50
			else: score = rr_sub50

			if i.reply_time <= 3600: score = score + rt_1
			elif i.reply_time <= 3600 * 4: score = score + rt_4
			elif i.reply_time <= 3600 * 12: score = score + rt_12
			elif i.reply_time <= 3600 * 24: score = score + rt_24
			elif i.reply_time <= 3600 * 48: score = score + rt_48
			elif i.reply_time <= 3600 * 24 * 7: score = score + rt_1w
			else: score = score + rt_super1w
			i._responsive_score= score
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
			notifs = Requests.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24)))
			for n in notifs:
				if n.state == 'P':
					n24 = n24 + 1
			notifs = Invites.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24)))
			for n in notifs:
				if n.state == 'P':
					n24 = n24 + 1
			n1w = 0
			notifs = Requests.objects.filter(Q(receiver= prof)&Q(created__gte= (time.time() - 3600*24*7)))
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
			elif n1w < 10: score = score + pop_1w_5
			elif n1w < 15: score = score + pop_1w_10
			elif n1w < 20: score = score + pop_1w_15
			elif n1w < 25: score = score + pop_1w_20
			elif n1w < 30: score = score + pop_1w_25
			elif n1w < 50: score = score + pop_1w_30
			elif n1w < 70: score = score + pop_1w_50
			else: score = score + pop_1w_70

			i._reqinv_score = score
		return data

	def sum_score(self, obj):
		obj._final_score = obj._reqinv_score + obj._responsive_score + obj._experience_score
		return obj

	def order_by_relevance_score(self, data):
		data = self.score_experience(data)
		data = self.score_responsive(data)
		data = self.score_reqinv(data)
		data = [self.sum_score(i) for i in data]
		return sorted(data, key=attrgetter('_final_score'), reverse=True)

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
			idx_old = idx_old + 1

		while idx_new < length:
			if new[idx_new] not in final:
				final.append(new[idx_new])
			idx_new = idx_new + 1
		return final

	def order_by_relevance(self):		
		#Split onlines and offlines
		online = [i for i in self.objects if i.online == True]
		offline = [i for i in self.objects if i.online == False]
		
		online = self.order_by_relevance_plus_news(online)
		offline = self.order_by_relevance_plus_news(offline)

		self.objects= online + offline

	################

	def order_by_avatar(self, people):
		avatar = []
		no_avatar = []

		for i in people:
			if 'blank_avatar' in i.avatar:
				no_avatar.append(i)
			else:
				avatar.append(i)
		return avatar, no_avatar

	def order_by_album(self, people):
		for i in people:
			i._photos = min(i.n_photos, settings.MAX_UPLOADED_PHOTOS) * settings.PHOTO_SCORE

		return people

	def order_by_profile(self, people):
		for i in people:
			completeness = 0
			prof = UserProfile.objects.get(pk=i.profile_id)
			#import pdb; pdb.set_trace()
			if len(prof.interested_in.all()) > 0: completeness = completeness + 1
			if prof.civil_state != '': completeness = completeness + 1
			if prof.all_about_you != '': completeness = completeness + 1
			if prof.main_mission != '': completeness = completeness + 1
			if prof.occupation != '': completeness = completeness + 1
			if len(prof.universities.all()) > 0: completeness = completeness + 1
			if prof.personal_philosophy != '': completeness = completeness + 1
			if prof.political_opinion != '': completeness = completeness + 1
			if prof.religion != '': completeness = completeness + 1
			if prof.enjoy_people != '': completeness = completeness + 1
			if prof.movies != '': completeness = completeness + 1
			if prof.sports != '': completeness = completeness + 1
			if prof.other_pages != '': completeness = completeness + 1
			if prof.sharing != '': completeness = completeness + 1
			if prof.incredible != '': completeness = completeness + 1
			if prof.inspired_by != '': completeness = completeness + 1
			if prof.quotes != '': completeness = completeness + 1
			if prof.current_city is None: completeness = completeness + 1
			if prof.hometown is None: completeness = completeness + 1

			if completeness >= 16: 
				i._prof_complete = settings.PROFILE_75
			elif completeness >= 10: 
				i._prof_complete = settings.PROFILE_50
			elif completeness >= 5: 
				i._prof_complete = settings.PROFILE_25
			else: 
				i._prof_complete = 0
		return people

	def order_by_recent(self, people):
		#import pdb; pdb.set_trace()
		now = datetime.now()		
		for i in people:
			usr = User.objects.get(pk=i.profile_id)
			if (now - timedelta(hours=12)).replace(tzinfo=utc) <= usr.last_login: 
				i._recent = settings.RECENT_12H
			elif (now - timedelta(days=2)).replace(tzinfo=utc) <= usr.last_login:  
				i._recent = settings.RECENT_2D
			elif (now - timedelta(weeks=1)).replace(tzinfo=utc) <= usr.last_login:  
				i._recent = settings.RECENT_1W
			else:
				i._recent = 0
		return people

	def sum_people_score(self, people):		
		for i in people:			
			i._final_score = i._photos + i._prof_complete + i._recent

		if len(people) > 0: return sorted(people, key=lambda x: x._final_score, reverse=False)
		#import pdb; pdb.set_trace()
		return []

	def order_by_people_relevance(self):
		online = [i for i in self.objects if i.online == True]
		offline = [i for i in self.objects if i.online == False]

		on_avatar, on_noavatar = self.order_by_avatar(online)
		off_avatar, off_noavatar = self.order_by_avatar(offline)

		on_avatar = self.order_by_album(on_avatar)
		on_noavatar = self.order_by_album(on_noavatar)
		off_avatar = self.order_by_album(off_avatar)
		off_noavatar = self.order_by_album(off_noavatar)

		on_avatar = self.order_by_profile(on_avatar)
		on_noavatar = self.order_by_profile(on_noavatar)
		off_avatar = self.order_by_profile(off_avatar)
		off_noavatar = self.order_by_profile(off_noavatar)

		off_avatar = self.order_by_recent(off_avatar)
		off_noavatar = self.order_by_recent(off_noavatar)

		return self.sum_people_score(on_avatar) + self.sum_people_score(on_noavatar) + self.sum_people_score(off_avatar) + self.sum_people_score(off_noavatar)

	def make_dirty(self):
		import string, random

		for i in self.objects:
			if i.first_name is not None:
				len_fn = len(i.first_name)
				i.first_name = [random.choice(string.ascii_lowercase) for n in xrange(len_fn)]
				i.first_name = "".join(i.first_name)
				i.first_name = i.first_name.capitalize()

			if i.last_name is not None:
				len_ln = len(i.last_name)
				i.last_name = [random.choice(string.ascii_lowercase) for n in xrange(len_ln)]
				i.last_name = "".join(i.last_name)
				i.last_name = i.last_name.capitalize()

			i.profile_id = None

class EditProfileObject(object):

	def __init__(self):
		self.interested_in = []
		self.hometown = {}
		self.reply_time = None
		self.main_mission = None
		self.birth_month = None
		self.civil_state = None
		self.personal_philosophy = None
		self.last_login_date = None
		self.education = []
		self.id = None
		self.occupation = None
		self.current = {}
		self.pw_state = None
		self.incredible = None
		self.other_locations = []
		self.sports = None
		self.languages = []
		self.birth_year = None
		self.quotes = None
		self.social_networks = []
		self.online = None
		self.sharing = None
		self.resource_uri = None
		self.pw_opinion = None
		self.political_opinion = None
		self.company = None
		self.reply_rate = None
		self.instant_messages = []
		self.phone = None
		self.active = None
		self.emails = None
		self.inspired_by = None
		self.other_pages = None
		self.first_name = None
		self.enjoy_people = None
		self.gender = None
		self.age = None
		self.all_about_you = None
		self.movies = None
		self.birth_day = None
		self.avatar = None
		self.last_login = {}
		self.last_name = None
		self.religion = None
		self.show_birthday = None
		self.albums = []

	def jsonable(self):
		res = dict()			
		for key, value in self.__dict__.items():   
			if value is not None and not key.startswith('ctrl_'):       
				res[key] = value
		return res

class PreviewProfileObject(object):

	def __init__(self):
		self.interested_in = []
		self.hometown = {}
		self.reply_time = None
		self.main_mission = None
		self.birth_month = None
		self.civil_state = None
		self.personal_philosophy = None
		self.last_login_date = None
		self.education = []
		self.id = None
		self.occupation = None
		self.current = {}
		self.pw_state = None
		self.incredible = None
		self.other_locations = []
		self.sports = None
		self.languages = []
		self.birth_year = None
		self.quotes = None
		self.online = None
		self.sharing = None
		self.resource_uri = None
		self.pw_opinion = None
		self.political_opinion = None
		self.company = None
		self.reply_rate = None
		self.active = None
		self.inspired_by = None
		self.other_pages = None
		self.first_name = None
		self.enjoy_people = None
		self.gender = None
		self.age = None
		self.all_about_you = None
		self.movies = None
		self.birth_day = None
		self.avatar = None
		self.last_login = {}
		self.last_name = None
		self.religion = None
		self.show_birthday = None
		self.albums = []

	def jsonable(self):
		res = dict()			
		for key, value in self.__dict__.items():   
			if value is not None and not key.startswith('ctrl_'):       
				res[key] = value
		return res


