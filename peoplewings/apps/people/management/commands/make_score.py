from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from people.models import UserProfile, PhotoAlbums, Photos
from django.db import transaction
from notifications.models import Requests, Invites, Notifications
from django.db.models import Q

import time
from datetime import datetime, timedelta
from django.utils.timezone import utc

from operator import attrgetter

class Command(BaseCommand):

	@transaction.commit_manually
	def handle(self, *args, **options):
		try:
			profiles = UserProfile.objects.all()
			for prof in profiles:
				experience = self.score_by_experience(prof)
				responsive = self.score_by_responsive(prof)
				reqinv = self.score_by_reqinv(prof)
				ambassator = self.score_by_ambassator(prof)
				recent = self.score_by_new(prof)
				avatar = self.score_by_avatar(prof)
				print '%s  Exp: %s, Response: %s, Reqinv: %s, Ambass: %s, Recent: %s, Avatar %s' % (prof.full_name, experience, responsive, reqinv, ambassator, recent, avatar)
				prof.search_score = experience + responsive + reqinv + ambassator + recent + avatar
				prof.save()
			transaction.commit()
		except Exception, e:
			transaction.rollback()
			raise CommandError("PPWERROR while updating search score: %s\n" %e)
		self.stdout.write("Search score updated succesfully\n")

	def score_by_experience(self, prof):
		photo_score = getattr(settings, 'PHOTO_SCORE', 0)
		max_photos = getattr(settings, 'MAX_UPLOADED_PHOTOS', 0)

		score = Photos.objects.filter(author = prof).count() * photo_score
		if photo_score * max_photos >= score:
			return score
		else:
			return photo_score * max_photos

	def score_by_responsive(self, prof):
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

		score = 0
		if prof.reply_rate == 100: score = rr_100
		elif prof.reply_rate >= 90: score = rr_90
		elif prof.reply_rate >= 80: score = rr_80
		elif prof.reply_rate >= 70: score = rr_70
		elif prof.reply_rate >= 60: score = rr_60
		elif prof.reply_rate >= 50: score = rr_50
		else: score = rr_sub50

		if prof.reply_time == -1:
			return score

		if prof.reply_time <= 3600: score = score + rt_1
		elif prof.reply_time <= 3600 * 4: score = score + rt_4
		elif prof.reply_time <= 3600 * 12: score = score + rt_12
		elif prof.reply_time <= 3600 * 24: score = score + rt_24
		elif prof.reply_time <= 3600 * 48: score = score + rt_48
		elif prof.reply_time <= 3600 * 24 * 7: score = score + rt_1w
		else: score = score + rt_super1w

		return score

	def score_by_reqinv(self, prof):
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

		score = 0
		n24 = 0
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

		return score

	def score_by_ambassator(self, prof):
		ambassator_score = getattr(settings, 'AMBASSATOR', 0)

		return ambassator_score if prof.ambassator else 0

	def score_by_new(self, prof):
		recent_3h = getattr(settings, 'RECENT_3H', 0)
		recent_12h = getattr(settings, 'RECENT_12H', 0)
		recent_2d = getattr(settings, 'RECENT_2D', 0)
		recent_1w = getattr(settings, 'RECENT_1W', 0)

		now = datetime.now()
		if (now - timedelta(hours=3)).replace(tzinfo=utc) <= prof.user.date_joined:
			return recent_3h

		if (now - timedelta(hours=12)).replace(tzinfo=utc) <= prof.user.date_joined:
			return recent_12h

		if (now - timedelta(days=2)).replace(tzinfo=utc) <= prof.user.date_joined:
			return recent_2d

		if (now - timedelta(weeks=1)).replace(tzinfo=utc) <= prof.user.date_joined:
			return recent_1w

		return 0

	def score_by_avatar(self, prof):
		def_avatar = getattr(settings, 'ANONYMOUS_BIG', '')
		has_avatar = 1000
		if prof.avatar == def_avatar:
			return 0
		return has_avatar




