"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import string
import random
import json
from datetime import datetime

from django.test import TestCase, Client
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.notifications.models import Notifications, Messages
from django.contrib.auth.models import User
from people.models import UserProfile
from peoplewings.libs.customauth.models import ApiToken

from django.utils.timezone import utc

 
class AutocompleteTest(TestCase):

	def setUp(self):
		self.user1 = G(User, first_name='Joan', last_name='Roca')
		self.profile1 = G(UserProfile, user=self.user1)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		self.user2 = G(User, first_name='Ezequiel', last_name='Anakyn')
		self.profile2 = G(UserProfile, user=self.user2)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		self.user3 = G(User, first_name='Eleonor', last_name='Lopez')
		self.profile3 = G(UserProfile, user=self.user3)
		self.token3 = ApiToken.objects.create(user=self.profile3.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

	def test_autocomplete_notification(self):
		c = Client()
		
		#check that initially empty lists are retrieved for all existing users
		r1 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']), 0)

		r2 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(json.loads(r2.content)['code'], 200)
		self.assertEqual(json.loads(r2.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r2.content)['status'], True)
		self.assertEqual(len(json.loads(r2.content)['data']), 0)

		r3 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token3, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 200)
		self.assertEqual(json.loads(r3.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r3.content)['status'], True)
		self.assertEqual(len(json.loads(r3.content)['data']), 0)
		
		# profile 1 sends a message to profile 2
		content = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		r3 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "message", "data": {"content": content}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')

		#check that for users 1 and 2 calling to autocomplete will give the other user's name and last name, and an empty list for user 3
		r1 = c.get('/ajax/search/notification_addressee?type=message&name=a', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']), 1)
		l1 = json.loads(r1.content)['data']
		self.assertEqual(l1[0]['first_name'], self.profile2.user.first_name)
		self.assertEqual(l1[0]['last_name'], self.profile2.user.last_name)
		self.assertEqual(l1[0]['id'], self.profile2.id)

		r1 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']), 0)

		r2 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(json.loads(r2.content)['code'], 200)
		self.assertEqual(json.loads(r2.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r2.content)['status'], True)
		self.assertEqual(len(json.loads(r2.content)['data']), 1)
		l2 = json.loads(r2.content)['data']
		self.assertEqual(l2[0]['first_name'], self.profile1.user.first_name)
		self.assertEqual(l2[0]['last_name'], self.profile1.user.last_name)
		self.assertEqual(l2[0]['id'], self.profile1.id)

		r2 = c.get('/ajax/search/notification_addressee?type=message&name=A', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(json.loads(r2.content)['code'], 200)
		self.assertEqual(json.loads(r2.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r2.content)['status'], True)
		self.assertEqual(len(json.loads(r2.content)['data']), 0)

		r3 = c.get('/ajax/search/notification_addressee?type=message&name=A', HTTP_X_AUTH_TOKEN=self.token3, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 200)
		self.assertEqual(json.loads(r3.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r3.content)['status'], True)
		self.assertEqual(len(json.loads(r3.content)['data']), 0)

		# profile 3 sends a message to profile 1
		content = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		r3 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile1.pk, "kind": "message", "data": {"content": content}}), HTTP_X_AUTH_TOKEN=self.token3, content_type='application/json')
		
		#check that for user 1, calling to autocomplete will give users' 2 and 3 name and last name, and for users 2 and 3 will return user's 1 name and last name
		r1 = c.get('/ajax/search/notification_addressee?type=message&name=E', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']), 2)
		l1 = json.loads(r1.content)['data']
		self.assertEqual(l1[0]['first_name'], self.profile2.user.first_name)
		self.assertEqual(l1[0]['last_name'], self.profile2.user.last_name)
		self.assertEqual(l1[0]['id'], self.profile2.id)
		self.assertEqual(l1[1]['first_name'], self.profile3.user.first_name)
		self.assertEqual(l1[1]['last_name'], self.profile3.user.last_name)
		self.assertEqual(l1[1]['id'], self.profile3.id)

		r1 = c.get('/ajax/search/notification_addressee?type=message&name=Ez', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']), 1)
		l1 = json.loads(r1.content)['data']
		self.assertEqual(l1[0]['first_name'], self.profile2.user.first_name)
		self.assertEqual(l1[0]['last_name'], self.profile2.user.last_name)
		self.assertEqual(l1[0]['id'], self.profile2.id)

		r2 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(json.loads(r2.content)['code'], 200)
		self.assertEqual(json.loads(r2.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r2.content)['status'], True)
		self.assertEqual(len(json.loads(r2.content)['data']), 1)
		l2 = json.loads(r2.content)['data']
		self.assertEqual(l2[0]['first_name'], self.profile1.user.first_name)
		self.assertEqual(l2[0]['last_name'], self.profile1.user.last_name)
		self.assertEqual(l2[0]['id'], self.profile1.id)

		r3 = c.get('/ajax/search/notification_addressee?type=message&name=J', HTTP_X_AUTH_TOKEN=self.token3, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 200)
		self.assertEqual(json.loads(r3.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r3.content)['status'], True)
		self.assertEqual(len(json.loads(r3.content)['data']), 1)
		l3 = json.loads(r3.content)['data']
		self.assertEqual(l2, l3)

		# check empty list according to name parameter
		r3 = c.get('/ajax/search/notification_addressee?type=message&name=Ju', HTTP_X_AUTH_TOKEN=self.token3, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 200)
		self.assertEqual(json.loads(r3.content)['msg'], "Candidates retrieved successfully.")
		self.assertEqual(json.loads(r3.content)['status'], True)
		self.assertEqual(len(json.loads(r3.content)['data']), 0)

		# check that an invalid type returns error
		r3 = c.get('/ajax/search/notification_addressee?type=messy', HTTP_X_AUTH_TOKEN=self.token3, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 400)
		self.assertEqual(json.loads(r3.content)['error'], 'Type not valid.')
		self.assertEqual(json.loads(r3.content)['status'], False)
