"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import string
import random
import json
from datetime import datetime
import uuid
import time

from django.test import TestCase, Client
from django_dynamic_fixture import G, get, F
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.notifications.models import Notifications, Messages, Requests, Invites, AccomodationInformation, NotificationsAlarm
from notifications.domain import Automata
from wings.models import Accomodation, Wing
from locations.models import City
from django.contrib.auth.models import User
from people.models import UserProfile
from peoplewings.libs.customauth.models import ApiToken

from django.utils.timezone import utc

 
class PaginationTest(TestCase):
	fixtures = ['locations.json', 'user.json', 'people.json', 'wings.json']

	
	def setUp(self):
		'''
		self.hadeer = User.objects.create_user(username = 'a@a.com', password = '123456'610
		self.ph = UserProfile.objects.create(user = self.hadeer, birthday="1987-03-04")

		self.john = User.objects.create_user(username = 'b@b.com', password = '123456')
		self.pj = UserProfile.objects.create(user = self.john, birthday="1987-03-04")

		self.n1 = Messages.objects.create(sender = self.pj, receiver = self.ph, reference="1")
		self.n2 = Messages.objects.create(sender = self.ph, receiver = self.pj, reference="1")

		self.n3 = Messages.objects.create(sender = self.ph, receiver = self.pj, reference="2")
		self.n4 = Messages.objects.create(sender = self.ph, receiver = self.pj, reference="2")
		self.n5 = Messages.objects.create(sender = self.pj, receiver = self.ph, reference="2")

		self.n6 = Messages.objects.create(sender = self.ph, receiver = self.pj, reference="3")
		self.n7 = Messages.objects.create(sender = self.ph, receiver = self.pj, reference="2")
		self.n8 = Messages.objects.create(sender = self.pj, receiver = self.ph, reference="3")

		'''
		self.eze = UserProfile.objects.get(user=User.objects.get(email='ezequiel@peoplewings.com'))
		self.joan = UserProfile.objects.get(user=User.objects.get(email='joan@peoplewings.com'))

		for i in range(5):
			Messages.objects.create(sender = self.eze, receiver = self.joan, reference=str(i))
		
	
 
	def test_models(self):

		self.eze = UserProfile.objects.get(user=User.objects.get(email='ezequiel@peoplewings.com'))
		self.joan = UserProfile.objects.get(user=User.objects.get(email='joan@peoplewings.com'))

		self.assertEqual(Notifications.objects.filter(receiver=self.eze).count(), Notifications.objects.filter(sender=self.joan).count())
		self.assertEqual(Notifications.objects.filter(receiver=self.eze).count(), 0)

		self.assertEqual(Notifications.objects.filter(sender=self.eze).count(), Notifications.objects.filter(receiver=self.joan).count())
		self.assertEqual(Notifications.objects.filter(sender=self.eze).count(), 5)

	def test_not_logged_in(self):
		c = Client()
		response = c.get('/api/v1/notificationslist', content_type='application/json')
		self.assertEqual(response.status_code, 401)
 
	def test_logged_in(self):
		c = Client()
		#c.login(username='Hadeer', password='123456')
		response = c.post('/api/v1/auth', json.dumps({ 'username' : 'ezequiel@peoplewings.com', 'password' : 'asdf'}), content_type='application/json')
		token = json.loads(response.content)['data']['xAuthToken']		
		response = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(json.loads(response.content)['status'], True)

	def test_pagination(self):
		c = Client()		
		response = c.post('/api/v1/auth', json.dumps({ 'username' : 'ezequiel@peoplewings.com', 'password' : 'asdf'}), content_type='application/json')
		token = json.loads(response.content)['data']['xAuthToken']		
		
		#check the first page exists
		r1 = c.get('/api/v1/notificationslist?page=1', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['msg'], "OK")
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['data']['count'], 5)
		self.assertEqual(json.loads(r1.content)['data']['endResult'], 5)
		self.assertEqual(json.loads(r1.content)['data']['startResult'], 1)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 5)
		l1 = json.loads(r1.content)['data']['items']

		#check that not providing the page parameter has the same effect as calling with page=1
		r2 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r2.content)['code'], 200)
		self.assertEqual(json.loads(r2.content)['msg'], "OK")
		self.assertEqual(json.loads(r2.content)['status'], True)
		self.assertEqual(json.loads(r2.content)['data']['count'], 5)
		self.assertEqual(json.loads(r2.content)['data']['endResult'], 5)
		self.assertEqual(json.loads(r2.content)['data']['startResult'], 1)
		self.assertEqual(len(json.loads(r2.content)['data']['items']), 5)
		l2 = json.loads(r2.content)['data']['items']
		self.assertEqual(l1, l2)

		#check last page
		r4 = c.get('/api/v1/notificationslist?page=1', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r4.content)['code'], 200)
		self.assertEqual(json.loads(r4.content)['msg'], "OK")
		self.assertEqual(json.loads(r4.content)['status'], True)
		self.assertEqual(json.loads(r4.content)['data']['count'], 5)
		self.assertEqual(json.loads(r4.content)['data']['endResult'], 5)
		self.assertEqual(json.loads(r4.content)['data']['startResult'], 1)
		self.assertEqual(len(json.loads(r4.content)['data']['items']), 5)

		# checking unexisting pages...
		r3 = c.get('/api/v1/notificationslist?page=4', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 413)
		self.assertEqual(json.loads(r3.content)['msg'], "Sorry, no results on that page.")
		self.assertEqual(json.loads(r3.content)['status'], False)

class GetListNotificationsTest(TestCase):
	def setUp(self):
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		self.profile2 = G(UserProfile)

		self.wing1 = G(Accomodation, author= self.profile1, city=G(City, name='Barcelona'))
		self.req = G(Requests, sender= self.profile2, receiver= self.profile1, first_sender=self.profile2, wing= self.wing1)

	def test_get(self):
		c = Client()
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 1)
		self.assertEqual(json.loads(r1.content)['data']['count'], 1)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), 1)
		first = items[0]
		self.assertTrue(isinstance(first, dict))
		self.assertTrue(first.has_key('wingParameters'))
		params = first['wingParameters']
		self.assertTrue(isinstance(params, dict))
		self.assertTrue(params.has_key('modified'))
		self.assertTrue(params.has_key('wingType'))
		self.assertTrue(params.has_key('message'))
		self.assertTrue(params.has_key('endDate'))
		self.assertTrue(params.has_key('startDate'))
		self.assertTrue(params.has_key('numPeople'))
		self.assertTrue(params.has_key('wingCity'))
		self.assertTrue(isinstance(params['modified'], list))
		self.assertEqual(len(params['modified']), 0)

		

class GetListMessagesTest(TestCase):

	def setUp(self):
		#make some messages as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		for i in range(100):
			self.msg1 = G(Messages, sender=self.profile1, reference = i%5)

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

	def test_get_messages(self):
		c = Client()
		#GET the messages
		r1 = c.get('/api/v1/notificationslist?kind=msg', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 5)
		self.assertEqual(json.loads(r1.content)['data']['count'], 5)

		
class PostListMessagesTest(TestCase):

	def setUp(self):
		#make some messages as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

	def test_post_messages(self):
		c = Client()
		content = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		#What happens?
		#Check that profile1 has no messages
		self.assertEqual(self.profile1.notifications_receiver.count(), 0)
		self.assertEqual(self.profile1.notifications_sender.count(), 0)
		#Check that profile2 has no messages
		self.assertEqual(self.profile2.notifications_receiver.count(), 0)
		self.assertEqual(self.profile2.notifications_sender.count(), 0)
		#When a user (profile1), sends a message to another user (profile2):
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "message", "data": {"content": content}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		#Response is well formed
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		#Profile 1 has 1 new message as a sender
		self.assertEqual(self.profile1.notifications_sender.count(), 1)
		#Profile 2 has 1 new message as a receiver
		self.assertEqual(self.profile2.notifications_receiver.count(), 1)
		#The message has a unique reference
		self.assertNotEqual(self.profile2.notifications_receiver.get().reference, None)
		#The message is well formed
		self.assertNotEqual(self.profile2.notifications_receiver.get().receiver, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().sender, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().created, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().kind, None)
		#The message has read = false
		self.assertEqual(self.profile2.notifications_receiver.get().read, False)
		#The first sender of the message is profile1
		self.assertEqual(self.profile2.notifications_receiver.get().first_sender, self.profile1)
		#Errors show up properly:
		#The receiver of the message does not exists
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": 10, "kind": "message", "data": {"content": content}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 403)
		self.assertEqual(json.loads(r1.content)['errors'], "The receiver of the message does not exists")
		#The message cannot be empty
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "message", "data": {"content": ""}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"content":"The message cannot be empty"})
		#The message is too long
		content = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(10000))
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "message", "data": {"content": content}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"content":"The message is too long"})

class PostListRequestsTest(TestCase):

	def setUp(self):
		#make some users and profiles as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token		

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		

	def test_post_requests(self):
		c = Client()
		self.wing2 = G(Accomodation, author=self.profile2)
		wing3 = G(Accomodation)
		private_message = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		public_message = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		make_public = False
		#What happens?
		#Check that profile1 has no requests
		self.assertEqual(self.profile1.notifications_receiver.count(), 0)
		self.assertEqual(self.profile1.notifications_sender.count(), 0)
		#Check that profile2 has no requests
		self.assertEqual(self.profile2.notifications_receiver.count(), 0)
		self.assertEqual(self.profile2.notifications_sender.count(), 0)
		#When a user (profile1), sends a request to another user (profile2):
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": private_message, "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		#Response is well formed
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		#Profile 1 has 1 new message as a sender
		self.assertEqual(self.profile1.notifications_sender.count(), 1)
		#Profile 2 has 1 new message as a receiver
		self.assertEqual(self.profile2.notifications_receiver.count(), 1)
		#The request has a unique reference
		self.assertNotEqual(self.profile2.notifications_receiver.get().reference, None)
		#The request is well formed
		self.assertNotEqual(self.profile2.notifications_receiver.get().receiver, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().sender, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().created, None)
		self.assertEqual(self.profile2.notifications_receiver.get().kind, "request")
		#The request has read = false
		self.assertEqual(self.profile2.notifications_receiver.get().read, False)
		#The first sender of the request is profile1
		self.assertEqual(self.profile2.notifications_receiver.get().first_sender, self.profile1)
		#As a request the state of it should be in "Pending"
		self.assertEqual(self.profile2.notifications_receiver.get().requests.state, "P")
		#As a request the wing should be the same we entered
		self.assertEqual(self.profile2.notifications_receiver.get().requests.wing.pk, self.wing2.pk)
		#As a request the public message should not be None or empty
		self.assertNotEqual(self.profile2.notifications_receiver.get().requests.public_message, None)
		#As a request the private message should not be None or empty
		self.assertNotEqual(self.profile2.notifications_receiver.get().requests.private_message, None)
		#We put make_public = false, we should check it
		self.assertNotEqual(self.profile2.notifications_receiver.get().requests.make_public, True)
		#We should check that profile1 does not have any wing with is_request = True
		test_public = None
		try:
			test_public = Wing.objects.get(author=self.profile1)
		except:
			pass
		if not make_public:
			self.assertEqual(test_public, None)
		else:
			self.assertNotEqual(test_public, None)
		#Check if the additional information (related with the wing, request and wing type) is correct
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get_or_none(), None)
		#Check if the start_date is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().start_date, None)
		#Check if the end_date is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().end_date, None)
		#Check if the transport is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().transport, None)
		#Check if the transport is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().num_people, None)		
		#Errors show up properly:
		#The receiver of the request does not exists
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": 456, "kind": "request",  "data": { "privateText": private_message, "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 403)
		self.assertEqual(json.loads(r1.content)['errors'], "The receiver of the request does not exists")
		#The request private message cannot be empty
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": "", "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"privateText" : "The request private message cannot be empty"})
		#The private message is too long
		private_message2 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(10000))
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": private_message2, "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"privateText" : "The request private message is too long"})
		#The public message is too long
		public_message2 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(10000))
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": private_message, "publicText": public_message2, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"publicText" : "The request public message is too long"})
		#Date start cannot be greater than date end
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": private_message, "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357562400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"endDate" : 'This field should be greater or equal than the starting date'})
		#The selected wing is not a valid choice
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": private_message, "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": wing3.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], 'The selected wing is not a valid choice')
		#Now we want to send a request with make public = True
		"""
		make_public = True
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "request",  "data": { "privateText": private_message, "publicText": public_message, "makePublic": make_public, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing2.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "arrivingVia": "Plane", "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		#We should check that profile1 does not have any wing with is_request = True
		test_public = None
		try:
			test_public = Wing.objects.get(author=self.profile1)
		except:
			pass
		if not make_public:
			self.assertEqual(test_public, None)
		else:
			self.assertNotEqual(test_public, None)
		"""

	def test_post_invites(self):
		c = Client()
		self.wing1 = G(Accomodation, author=self.profile1)
		wing3 = G(Accomodation)
		private_message = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		#What happens?
		#Check that profile1 has no requests
		self.assertEqual(self.profile1.notifications_receiver.count(), 0)
		self.assertEqual(self.profile1.notifications_sender.count(), 0)
		#Check that profile2 has no requests
		self.assertEqual(self.profile2.notifications_receiver.count(), 0)
		self.assertEqual(self.profile2.notifications_sender.count(), 0)
		#When a user (profile1), sends a invite to another user (profile2):
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "invite",  "data": { "privateText": private_message, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing1.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		#Response is well formed
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		#Profile 1 has 1 new message as a sender
		self.assertEqual(self.profile1.notifications_sender.count(), 1)
		#Profile 2 has 1 new message as a receiver
		self.assertEqual(self.profile2.notifications_receiver.count(), 1)
		#The invite has a unique reference
		self.assertNotEqual(self.profile2.notifications_receiver.get().reference, None)
		#The invite is well formed
		self.assertNotEqual(self.profile2.notifications_receiver.get().receiver, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().sender, None)
		self.assertNotEqual(self.profile2.notifications_receiver.get().created, None)
		self.assertEqual(self.profile2.notifications_receiver.get().kind, "invite")
		#The invite has read = false
		self.assertEqual(self.profile2.notifications_receiver.get().read, False)
		#The first sender of the invite is profile1
		self.assertEqual(self.profile2.notifications_receiver.get().first_sender, self.profile1)
		#As a invite the state of it should be in "Pending"
		self.assertEqual(self.profile2.notifications_receiver.get().invites.state, "P")
		#As a invite the wing should be the same we entered
		self.assertEqual(self.profile2.notifications_receiver.get().invites.wing.pk, self.wing1.pk)
		#As a invite the private message should not be None or empty
		self.assertNotEqual(self.profile2.notifications_receiver.get().invites.private_message, None)
		#Check if the additional information (related with the wing, request and wing type) is correct
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get_or_none(), None)
		#Check if the start_date is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().start_date, None)
		#Check if the end_date is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().end_date, None)
		#Check if the capacity is not null
		self.assertNotEqual(self.profile2.notifications_receiver.get().accomodationinformation_notification.get().num_people, None)		
		#Errors show up properly:
		#The receiver of the request does not exists
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": 456, "kind": "invite",  "data": { "privateText": private_message, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing1.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2,  "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 403)
		self.assertEqual(json.loads(r1.content)['errors'], "The receiver of the request does not exists")
		#The request private message cannot be empty
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "invite",  "data": { "privateText": "", "wingType": "accomodation",   "wingParameters": {"wingId": self.wing1.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"privateText" : "The request private message cannot be empty"})
		#The private message is too long
		private_message2 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(10000))
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "invite",  "data": { "privateText": private_message2, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing1.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2, "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"privateText" : "The request private message is too long"})
		#Date start cannot be greater than date end
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "invite",  "data": { "privateText": private_message, "wingType": "accomodation",   "wingParameters": {"wingId": self.wing1.pk, "startDate": "1357603200", "endDate": "1357562400", "capacity": 2, "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], {"endDate" : 'This field should be greater or equal than the starting date'})
		#The selected wing is not a valid choice
		r1 = c.post('/api/v1/notificationslist', json.dumps({"idReceiver": self.profile2.pk, "kind": "invite",  "data": { "privateText": private_message, "wingType": "accomodation",   "wingParameters": {"wingId": wing3.pk, "startDate": "1357603200", "endDate": "1357862400", "capacity": 2,  "flexibleStart": False, "flexibleEnd": False}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 410)
		self.assertEqual(json.loads(r1.content)['errors'], 'The selected wing is not a valid choice')

class DeleteNotificationsTest(TestCase):

	def setUp(self):
		#make some users and profiles as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token		

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

	def test_delete_notifications(self):
		#Initialize method vars
		request1 = G(Requests, receiver=self.profile1, first_sender = self.profile1)
		request2 = G(Requests, sender=self.profile1)
		invite1 = G(Invites, receiver=self.profile1, first_sender = self.profile1)
		message1 = G(Messages, sender=self.profile1)
		request3 = G(Requests, receiver=self.profile2, sender = self.profile1, first_sender = self.profile2)
		message2 = G(Messages, sender=self.profile2)
		invite2 = G(Invites)
		c = Client()

		#Initial checks...
		#Check profile 1 has 5 notifications
		count = 0
		for i in self.profile1.notifications_receiver.all():
			if i.first_sender.pk == self.profile1.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		for i in self.profile1.notifications_sender.all():
			if i.first_sender.pk == self.profile1.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		self.assertEqual(count, 5)
		#Check profile 2 has 2 notifications
		count = 0
		for i in self.profile2.notifications_receiver.all():
			if i.first_sender.pk == self.profile2.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		for i in self.profile2.notifications_sender.all():
			if i.first_sender.pk == self.profile2.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		self.assertEqual(count, 2)
		#Make the call that deletes request1, message1 and request3 from the profile1 POV
		r1 = c.put('/api/v1/notificationslist', json.dumps({"threads": [request1.reference, request3.reference, message1.reference]}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(json.loads(r1.content)['data'], 'The notifications have been deleted succesfully')

		#When deleting a notification thread, we make it "invisible", to the user. So...
		count = 0
		for i in self.profile1.notifications_receiver.all():
			if i.first_sender.pk == self.profile1.pk:
				if i.first_sender_visible == True:					
					count = count + 1
			else:
				if i.second_sender_visible == True:					
					count = count + 1
		for i in self.profile1.notifications_sender.all():
			if i.first_sender.pk == self.profile1.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		self.assertEqual(count, 2)
		#And the other one, profile2, keeps seeing 2 notification
		count = 0
		for i in self.profile2.notifications_receiver.all():
			if i.first_sender.pk == self.profile2.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		for i in self.profile2.notifications_sender.all():
			if i.first_sender.pk == self.profile2.pk:
				if i.first_sender_visible == True:
					count = count + 1
			else:
				if i.second_sender_visible == True:
					count = count + 1
		self.assertEqual(count, 2)
		#We will need to check the other methods (GET /api/v1/notificationslist) to see if they implement this functionality as well. The result should be the same
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 2)
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 2)
		#ERRORS
		uuid_1 = str(uuid.uuid4())
		uuid_2 = str(uuid.uuid4())
		r1 = c.put('/api/v1/notificationslist', json.dumps({"threads": [uuid_1, uuid_2, message1.reference, message2.reference, invite2.reference]}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], False)
		self.assertEqual(json.loads(r1.content)['code'], 400)
		self.assertEqual(json.loads(r1.content)['errors'], {message2.reference : "This reference is not owned by the user thus it can't be deleted", invite2.reference : "This reference is not owned by the user thus it can't be deleted"})

class GetNotificationsThreadTest(TestCase):

	def setUp(self):
		#make some users and profiles as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token		

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

		#First make a thread of messages
		self.ref = str(uuid.uuid4())
		self.created = time.time() - 3600*24
		self.check_created = self.created
		self.message1 = G(Messages, reference = self.ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message2 = G(Messages, reference = self.ref, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message3 = G(Messages, reference = self.ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message4 = G(Messages, reference = self.ref, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message5 = G(Messages, reference = self.ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message6 = G(Messages, reference = self.ref, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message7 = G(Messages, reference = self.ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="message", created=self.created)
		self.created = self.created + 3600
		self.message8 = G(Messages, reference = self.ref, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="message", created=self.created)

		#Make another thread of messages belonging to profile2 and profile 3
		self.profile3 = G(UserProfile)
		self.ref2 = str(uuid.uuid4())
		self.created2 = time.time() - 3600*24
		self.check_created2 = self.created
		self.message11 = G(Messages, reference = self.ref2, sender=self.profile2, receiver=self.profile3, first_sender=self.profile2, kind="message", created=self.created2)
		self.created = self.created + 3600
		self.message12 = G(Messages, reference = self.ref2, sender=self.profile3, receiver=self.profile2, first_sender=self.profile2, kind="message", created=self.created2)
		self.created = self.created + 3600
		self.message13 = G(Messages, reference = self.ref2, sender=self.profile2, receiver=self.profile3, first_sender=self.profile2, kind="message", created=self.created2)

		#Make a thread of requests
		self.ref3 = str(uuid.uuid4())
		self.created3 = time.time() - 3600*24
		self.start_date_req = 123923488234
		self.end_date_req = 123943488234
		self.check_created3 = self.created3
		self.check_created3_static = self.check_created3
		self.wingreq = G(Accomodation, author= self.profile2)
		self.request1 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='P', wing= self.wingreq, read=True)
		accominfo1 = G(AccomodationInformation, notification=self.request1, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600
		self.request2 = G(Requests, reference = self.ref3, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="request", created=self.created3, state='A', wing= self.wingreq, read=True)
		accominfo2 = G(AccomodationInformation, notification=self.request2, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600
		self.request3 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='A', wing= self.wingreq, read=True)
		accominfo3 = G(AccomodationInformation, notification=self.request3, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600
		self.request4 = G(Requests, reference = self.ref3, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="request", created=self.created3, state='A', wing= self.wingreq, read=True)
		accominfo4 = G(AccomodationInformation, notification=self.request4, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600
		self.request5 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='A', wing= self.wingreq, read=True)
		accominfo5 = G(AccomodationInformation, notification=self.request5, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600
		self.request6 = G(Requests, reference = self.ref3, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="request", created=self.created3, state='A', wing= self.wingreq, read=True)
		accominfo6 = G(AccomodationInformation, notification=self.request6, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600
		self.request7 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='A', wing= self.wingreq, read=False)
		accominfo7 = G(AccomodationInformation, notification=self.request7, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created3 + 3600

	def test_get_notificationsthread_message(self):
		#Initialize method vars
		c = Client()
		expected_sender = self.profile1
		expected_receiver = self.profile2

		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		#Now let's check out the data we've just received...
		#... we know that the notifications come ordered from older to newer (ASC)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertEqual(js['data'].has_key('reference'), True)
		self.assertEqual(data['reference'], self.ref)
		self.assertEqual(js['data'].has_key('kind'), True)
		self.assertEqual(data['kind'], 'message')
		self.assertEqual(js['data'].has_key('items'), True)
		self.assertEqual(isinstance(data['items'], list), True)				
		for i in data['items']:			
			#Check if the response is good
			self.assertTrue(i.has_key('senderId'))
			self.assertEqual(i['senderId'], expected_sender.pk)
			self.assertTrue(i.has_key('senderName'))
			self.assertEqual(i['senderName'], '%s %s' % (expected_sender.user.first_name, expected_sender.user.last_name))
			self.assertTrue(i.has_key('senderAge'))
			self.assertEqual(i['senderAge'], expected_sender.get_age())
			self.assertTrue(i.has_key('senderVerified'))
			self.assertEqual(i['senderVerified'], True)
			self.assertTrue(i.has_key('senderLocation'))
			self.assertEqual(i['senderLocation'], expected_sender.current_city.stringify())
			self.assertTrue(i.has_key('senderFriends'))
			self.assertEqual(i['senderFriends'], expected_sender.relationships.count())
			self.assertTrue(i.has_key('senderReferences'))
			self.assertEqual(i['senderReferences'], expected_sender.references.count())
			self.assertTrue(i.has_key('senderMedAvatar'))
			self.assertEqual(i['senderMedAvatar'], expected_sender.medium_avatar)
			self.assertTrue(i.has_key('senderSmallAvatar'))
			self.assertEqual(i['senderSmallAvatar'], expected_sender.thumb_avatar)
			self.assertTrue(i.has_key('senderConnected'))
			self.assertEqual(i['senderConnected'], 'F')
			self.assertTrue(i.has_key('receiverId'))
			self.assertEqual(i['receiverId'], expected_receiver.pk)
			self.assertTrue(i.has_key('receiverAvatar'))
			self.assertEqual(i['receiverAvatar'], expected_receiver.thumb_avatar)
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))
			self.assertTrue(i.has_key('created'))		
			self.assertEqual(i['created'], int(self.check_created))

			#Update next data
			if expected_sender.pk == self.profile1.pk:
				expected_sender = self.profile2
				expected_receiver = self.profile1
			else:
				expected_sender = self.profile1
				expected_receiver = self.profile2
			self.check_created = self.check_created + 3600

		#Now the ERRORS
		r1 = c.get('/api/v1/notificationsthread/' + str(uuid.uuid4()), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The notification with that reference does not exists")

		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref2), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "You are not allowed to visualize the notification with that reference")

	def test_get_notificationsthread_request(self):
		#Initialize method vars
		c = Client()

		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		#Now let's check out the data we've just received...
		#... we know that the notifications come ordered from older to newer (ASC)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(data.has_key('reference'), True)
		self.assertEqual(data['reference'], self.ref3)
		self.assertEqual(js['data'].has_key('kind'), True)
		self.assertEqual(data['kind'], 'request')
		self.assertEqual(js['data'].has_key('firstSender'), True)
		self.assertEqual(data['firstSender'], self.profile1.pk)
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], 'A')
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], self.wingreq.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], self.wingreq.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], self.wingreq.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], self.start_date_req)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], self.end_date_req)
			self.assertTrue(params.has_key('capacity'))
			self.assertTrue(params.has_key('arrivingVia'))
			self.assertTrue(params.has_key('flexibleStartDate'))
			self.assertTrue(params.has_key('flexibleEndDate'))
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))			

		self.assertEqual(data.has_key('options'), True)
		self.assertTrue(isinstance(data['options'], list))
		options = data['options']

		self.assertEqual(js['data'].has_key('items'), True)
		self.assertEqual(isinstance(data['items'], list), True)
		self.assertEqual(len(data['items']), 7)		

		expected_sender = self.profile1
		expected_receiver = self.profile2		
		for i in data['items']:			
			#Check if the response is good
			self.assertTrue(i.has_key('senderId'))
			self.assertEqual(i['senderId'], expected_sender.pk)
			self.assertTrue(i.has_key('senderName'))
			self.assertEqual(i['senderName'], '%s %s' % (expected_sender.user.first_name, expected_sender.user.last_name))
			self.assertTrue(i.has_key('senderAge'))
			self.assertEqual(i['senderAge'], expected_sender.get_age())
			self.assertTrue(i.has_key('senderVerified'))
			self.assertEqual(i['senderVerified'], True)
			self.assertTrue(i.has_key('senderLocation'))
			self.assertEqual(i['senderLocation'], expected_sender.current_city.stringify())
			self.assertTrue(i.has_key('senderFriends'))
			self.assertEqual(i['senderFriends'], expected_sender.relationships.count())
			self.assertTrue(i.has_key('senderReferences'))
			self.assertEqual(i['senderReferences'], expected_sender.references.count())
			self.assertTrue(i.has_key('senderMedAvatar'))
			self.assertEqual(i['senderMedAvatar'], expected_sender.medium_avatar)
			self.assertTrue(i.has_key('senderSmallAvatar'))
			self.assertEqual(i['senderSmallAvatar'], expected_sender.thumb_avatar)
			self.assertTrue(i.has_key('senderConnected'))
			self.assertEqual(i['senderConnected'], 'F')
			self.assertTrue(i.has_key('receiverId'))
			self.assertEqual(i['receiverId'], expected_receiver.pk)
			self.assertTrue(i.has_key('receiverAvatar'))
			self.assertEqual(i['receiverAvatar'], expected_receiver.thumb_avatar)
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))
			self.assertTrue(i.has_key('created'))		
			self.assertEqual(i['created'], int(self.check_created3))

			#Update next data
			if expected_sender.pk == self.profile1.pk:
				expected_sender = self.profile2
				expected_receiver = self.profile1
			else:
				expected_sender = self.profile1
				expected_receiver = self.profile2
			self.check_created3 = self.check_created3 + 3600

		#Now, for each request, we need to check that is correctly marked as read. The rule is simple, if prof1 reads reqthread1, all the messages that are not his should be marked as read.
		self.request1 = Requests.objects.get(pk = self.request1.pk)
		self.assertTrue(self.request1.read)
		self.request2 = Requests.objects.get(pk = self.request2.pk)
		self.assertTrue(self.request2.read)
		self.request3 = Requests.objects.get(pk = self.request3.pk)
		self.assertTrue(self.request3.read)
		self.request4 = Requests.objects.get(pk = self.request4.pk)
		self.assertTrue(self.request4.read)
		self.request5 = Requests.objects.get(pk = self.request5.pk)
		self.assertTrue(self.request5.read)
		self.request6 = Requests.objects.get(pk = self.request6.pk)
		self.assertTrue(self.request6.read)
		self.request7 = Requests.objects.get(pk = self.request7.pk)
		self.assertFalse(self.request7.read)
		#Now let's make profile2 read the same thread, this should mark request7 to "read"
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		#Now let's check out the data we've just received...
		#... we know that the notifications come ordered from older to newer (ASC)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))		
		self.assertEqual(data.has_key('reference'), True)
		self.assertEqual(data['reference'], self.ref3)
		self.assertEqual(js['data'].has_key('kind'), True)
		self.assertEqual(data['kind'], 'request')
		self.assertEqual(js['data'].has_key('firstSender'), True)
		self.assertEqual(data['firstSender'], self.profile1.pk)
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], 'A')
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], self.wingreq.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], self.wingreq.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], self.wingreq.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], self.start_date_req)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], self.end_date_req)
			self.assertTrue(params.has_key('capacity'))
			self.assertTrue(params.has_key('arrivingVia'))
			self.assertTrue(params.has_key('flexibleStartDate'))
			self.assertTrue(params.has_key('flexibleEndDate'))
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))

		self.assertEqual(data.has_key('options'), True)
		self.assertTrue(isinstance(data['options'], list))
		options = data['options']

		self.assertEqual(js['data'].has_key('items'), True)
		self.assertEqual(isinstance(data['items'], list), True)
		self.assertEqual(len(data['items']), 7)	

		expected_sender = self.profile1
		expected_receiver = self.profile2
		self.check_created3 = self.check_created3_static
		for i in data['items']:			
			#Check if the response is good
			self.assertTrue(i.has_key('senderId'))
			self.assertEqual(i['senderId'], expected_sender.pk)
			self.assertTrue(i.has_key('senderName'))
			self.assertEqual(i['senderName'], '%s %s' % (expected_sender.user.first_name, expected_sender.user.last_name))
			self.assertTrue(i.has_key('senderAge'))
			self.assertEqual(i['senderAge'], expected_sender.get_age())
			self.assertTrue(i.has_key('senderVerified'))
			self.assertEqual(i['senderVerified'], True)
			self.assertTrue(i.has_key('senderLocation'))
			self.assertEqual(i['senderLocation'], expected_sender.current_city.stringify())
			self.assertTrue(i.has_key('senderFriends'))
			self.assertEqual(i['senderFriends'], expected_sender.relationships.count())
			self.assertTrue(i.has_key('senderReferences'))
			self.assertEqual(i['senderReferences'], expected_sender.references.count())
			self.assertTrue(i.has_key('senderMedAvatar'))
			self.assertEqual(i['senderMedAvatar'], expected_sender.medium_avatar)
			self.assertTrue(i.has_key('senderSmallAvatar'))
			self.assertEqual(i['senderSmallAvatar'], expected_sender.thumb_avatar)
			self.assertTrue(i.has_key('senderConnected'))
			self.assertEqual(i['senderConnected'], 'F')
			self.assertTrue(i.has_key('receiverId'))
			self.assertEqual(i['receiverId'], expected_receiver.pk)
			self.assertTrue(i.has_key('receiverAvatar'))
			self.assertEqual(i['receiverAvatar'], expected_receiver.thumb_avatar)
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))
			self.assertTrue(i.has_key('created'))		
			self.assertEqual(i['created'], int(self.check_created3))

			#Update next data
			if expected_sender.pk == self.profile1.pk:
				expected_sender = self.profile2
				expected_receiver = self.profile1
			else:
				expected_sender = self.profile1
				expected_receiver = self.profile2
			self.check_created3 = self.check_created3 + 3600


		self.request1 = Requests.objects.get(pk = self.request1.pk)
		self.assertTrue(self.request1.read)
		self.request2 = Requests.objects.get(pk = self.request2.pk)
		self.assertTrue(self.request2.read)
		self.request3 = Requests.objects.get(pk = self.request3.pk)
		self.assertTrue(self.request3.read)
		self.request4 = Requests.objects.get(pk = self.request4.pk)
		self.assertTrue(self.request4.read)
		self.request5 = Requests.objects.get(pk = self.request5.pk)
		self.assertTrue(self.request5.read)
		self.request6 = Requests.objects.get(pk = self.request6.pk)
		self.assertTrue(self.request6.read)
		self.request7 = Requests.objects.get(pk = self.request7.pk)
		self.assertTrue(self.request7.read)

		#Now we are gonna create a new Pending request...
		self.ref3 = str(uuid.uuid4())
		self.created3 = time.time() - 3600*24
		self.check_created3_static = self.created3
		self.start_date_req = 123923588234
		self.end_date_req = 123943588234
		self.check_created3 = self.created3
		self.wingreq = G(Accomodation, author= self.profile2)
		self.request1 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='P', wing= self.wingreq)
		accominfo1 = G(AccomodationInformation, notification=self.request1, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created + 3600
		#Now we whould check the "options" for this request...
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		#Now let's check out the data we've just received...
		#... we know that the notifications come ordered from older to newer (ASC)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))		
		self.assertEqual(data.has_key('reference'), True)
		self.assertEqual(data['reference'], self.ref3)
		self.assertEqual(js['data'].has_key('kind'), True)
		self.assertEqual(data['kind'], 'request')
		self.assertEqual(js['data'].has_key('firstSender'), True)
		self.assertEqual(data['firstSender'], self.profile1.pk)
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], 'P')
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], self.wingreq.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], self.wingreq.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], self.wingreq.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], self.start_date_req)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], self.end_date_req)
			self.assertTrue(params.has_key('capacity'))
			self.assertTrue(params.has_key('arrivingVia'))
			self.assertTrue(params.has_key('flexibleStartDate'))
			self.assertTrue(params.has_key('flexibleEndDate'))
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))

		self.assertEqual(data.has_key('options'), True)
		self.assertTrue(isinstance(data['options'], list))
		options = data['options']

		self.assertEqual(js['data'].has_key('items'), True)
		self.assertEqual(isinstance(data['items'], list), True)
		self.assertEqual(len(data['items']), 1)		

		expected_sender = self.profile1
		expected_receiver = self.profile2		
		for i in data['items']:			
			#Check if the response is good
			self.assertTrue(i.has_key('senderId'))
			self.assertEqual(i['senderId'], expected_sender.pk)
			self.assertTrue(i.has_key('senderName'))
			self.assertEqual(i['senderName'], '%s %s' % (expected_sender.user.first_name, expected_sender.user.last_name))
			self.assertTrue(i.has_key('senderAge'))
			self.assertEqual(i['senderAge'], expected_sender.get_age())
			self.assertTrue(i.has_key('senderVerified'))
			self.assertEqual(i['senderVerified'], True)
			self.assertTrue(i.has_key('senderLocation'))
			self.assertEqual(i['senderLocation'], expected_sender.current_city.stringify())
			self.assertTrue(i.has_key('senderFriends'))
			self.assertEqual(i['senderFriends'], expected_sender.relationships.count())
			self.assertTrue(i.has_key('senderReferences'))
			self.assertEqual(i['senderReferences'], expected_sender.references.count())
			self.assertTrue(i.has_key('senderMedAvatar'))
			self.assertEqual(i['senderMedAvatar'], expected_sender.medium_avatar)
			self.assertTrue(i.has_key('senderSmallAvatar'))
			self.assertEqual(i['senderSmallAvatar'], expected_sender.thumb_avatar)
			self.assertTrue(i.has_key('senderConnected'))
			self.assertEqual(i['senderConnected'], 'F')
			self.assertTrue(i.has_key('receiverId'))
			self.assertEqual(i['receiverId'], expected_receiver.pk)
			self.assertTrue(i.has_key('receiverAvatar'))
			self.assertEqual(i['receiverAvatar'], expected_receiver.thumb_avatar)
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))
			self.assertTrue(i.has_key('created'))		
			self.assertEqual(i['created'], int(self.check_created3))

			#Update next data
			if expected_sender.pk == self.profile1.pk:
				expected_sender = self.profile2
				expected_receiver = self.profile1
			else:
				expected_sender = self.profile1
				expected_receiver = self.profile2
			self.check_created3 = self.check_created3 + 3600

		#Now, for each request, we need to check that is correctly marked as read. The rule is simple, if prof1 reads reqthread1, all the messages that are not his should be marked as read.
		self.assertFalse(self.request1.read)
		#Then check the same for profile2...
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		#Now let's check out the data we've just received...
		#... we know that the notifications come ordered from older to newer (ASC)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))		
		self.assertEqual(data.has_key('reference'), True)
		self.assertEqual(data['reference'], self.ref3)
		self.assertEqual(js['data'].has_key('kind'), True)
		self.assertEqual(data['kind'], 'request')
		self.assertEqual(js['data'].has_key('firstSender'), True)
		self.assertEqual(data['firstSender'], self.profile1.pk)
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], 'P')
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], self.wingreq.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], self.wingreq.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], self.wingreq.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], self.start_date_req)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], self.end_date_req)
			self.assertTrue(params.has_key('capacity'))
			self.assertTrue(params.has_key('arrivingVia'))
			self.assertTrue(params.has_key('flexibleStartDate'))
			self.assertTrue(params.has_key('flexibleEndDate'))
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))

		self.assertEqual(data.has_key('options'), True)
		self.assertTrue(isinstance(data['options'], list))
		options = data['options']

		self.assertEqual(js['data'].has_key('items'), True)
		self.assertEqual(isinstance(data['items'], list), True)
		self.assertEqual(len(data['items']), 1)	

		expected_sender = self.profile1
		expected_receiver = self.profile2
		self.check_created3 = self.check_created3_static
		for i in data['items']:			
			#Check if the response is good
			self.assertTrue(i.has_key('senderId'))
			self.assertEqual(i['senderId'], expected_sender.pk)
			self.assertTrue(i.has_key('senderName'))
			self.assertEqual(i['senderName'], '%s %s' % (expected_sender.user.first_name, expected_sender.user.last_name))
			self.assertTrue(i.has_key('senderAge'))
			self.assertEqual(i['senderAge'], expected_sender.get_age())
			self.assertTrue(i.has_key('senderVerified'))
			self.assertEqual(i['senderVerified'], True)
			self.assertTrue(i.has_key('senderLocation'))
			self.assertEqual(i['senderLocation'], expected_sender.current_city.stringify())
			self.assertTrue(i.has_key('senderFriends'))
			self.assertEqual(i['senderFriends'], expected_sender.relationships.count())
			self.assertTrue(i.has_key('senderReferences'))
			self.assertEqual(i['senderReferences'], expected_sender.references.count())
			self.assertTrue(i.has_key('senderMedAvatar'))
			self.assertEqual(i['senderMedAvatar'], expected_sender.medium_avatar)
			self.assertTrue(i.has_key('senderSmallAvatar'))
			self.assertEqual(i['senderSmallAvatar'], expected_sender.thumb_avatar)
			self.assertTrue(i.has_key('senderConnected'))
			self.assertEqual(i['senderConnected'], 'F')
			self.assertTrue(i.has_key('receiverId'))
			self.assertEqual(i['receiverId'], expected_receiver.pk)
			self.assertTrue(i.has_key('receiverAvatar'))
			self.assertEqual(i['receiverAvatar'], expected_receiver.thumb_avatar)
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))
			self.assertTrue(i.has_key('created'))		
			self.assertEqual(i['created'], int(self.check_created3))

			#Update next data
			if expected_sender.pk == self.profile1.pk:
				expected_sender = self.profile2
				expected_receiver = self.profile1
			else:
				expected_sender = self.profile1
				expected_receiver = self.profile2
			self.check_created3 = self.check_created3 + 3600

		self.request1 = Requests.objects.get(pk = self.request1.pk)
		self.assertTrue(self.request1.read)
		#Let's only check the tree of options
		self.ref3 = str(uuid.uuid4())
		self.created3 = time.time() - 3600*24
		self.check_created3_static = self.created3
		self.start_date_req = 123923588234
		self.end_date_req = 123943588234
		self.check_created3 = self.created3
		self.wingreq = G(Accomodation, author= self.profile2)
		self.request1 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='P', wing= self.wingreq)
		accominfo1 = G(AccomodationInformation, notification=self.request1, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created + 3600
		self.request2 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='D', wing= self.wingreq)
		accominfo2 = G(AccomodationInformation, notification=self.request2, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created + 3600
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		options = json.loads(r1.content)['data']['options']
		self.assertEqual(options, ['Pending', 'Chat'])
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		options = json.loads(r1.content)['data']['options']
		self.assertEqual(options, ['Chat'])

		self.ref3 = str(uuid.uuid4())
		self.created3 = time.time() - 3600*24
		self.check_created3_static = self.created3
		self.start_date_req = 123923588234
		self.end_date_req = 123943588234
		self.check_created3 = self.created3
		self.wingreq = G(Accomodation, author= self.profile2)
		self.request1 = G(Requests, reference = self.ref3, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=self.created3, state='P', wing= self.wingreq)
		accominfo1 = G(AccomodationInformation, notification=self.request1, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created + 3600
		self.request2 = G(Requests, reference = self.ref3, sender=self.profile2, receiver=self.profile1, first_sender=self.profile1, kind="request", created=self.created3, state='D', wing= self.wingreq)
		accominfo2 = G(AccomodationInformation, notification=self.request2, modified= False, start_date = self.start_date_req, end_date= self.end_date_req)
		self.created3 = self.created + 3600
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		options = json.loads(r1.content)['data']['options']
		self.assertEqual(options, ['Chat'])
		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref3), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		options = json.loads(r1.content)['data']['options']
		self.assertEqual(options, ['Accept', 'Maybe', 'Chat'])

		#Now the ERRORS
		r1 = c.get('/api/v1/notificationsthread/' + str(uuid.uuid4()), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The notification with that reference does not exists")

		r1 = c.get('/api/v1/notificationsthread/' + str(self.ref2), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "You are not allowed to visualize the notification with that reference")

class PostNotificationsThreadTest(TestCase):

	def setUp(self):
		#make some users and profiles as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token		

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token


	def test_post_message(self):
		#Initialize variables
		c = Client()
		content1 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content2 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content3 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content4 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(10000))
		#First make a thread of messages
		ref = str(uuid.uuid4())
		created = time.time() - 3600*24
		check_created = created
		message1 = G(Messages, reference = ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="message", created=created, private_message = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200)))

		#First make a thread of messages
		ref2 = str(uuid.uuid4())
		created = time.time() - 3600*24
		check_created = created
		message2 = G(Messages, reference = ref2, kind="message", created=created, private_message = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200)))
		#Check if profile1 has 1 message and profile2 has 1 message as well...
		self.assertEqual(len(self.profile1.notifications_sender.all()) + len(self.profile1.notifications_receiver.all()), 1)
		self.assertEqual(len(self.profile2.notifications_sender.all()) + len(self.profile2.notifications_receiver.all()), 1)

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Message sent succesfully")

		#Then we are gonna check if the message has been sent...
		#Check if profile1 has 2 message and profile2 has 2 message as well...
		self.assertEqual(len(self.profile1.notifications_sender.all()) + len(self.profile1.notifications_receiver.all()), 2)
		self.assertEqual(len(self.profile2.notifications_sender.all()) + len(self.profile2.notifications_receiver.all()), 2)
		#Check if the newest message is the one we've just sended
		msg = Messages.objects.filter(reference = ref).order_by('created')[1]
		self.assertEqual(msg.private_message, content1)
		self.assertEqual(msg.reference, ref)
		#Check if its ordered correctly (oldest first)
		self.assertEqual(msg.private_message, content1)
		self.assertEqual(msg.read, False)
		self.assertEqual(msg.kind, 'message')
		self.assertEqual(msg.first_sender, self.profile1)
		self.assertEqual(msg.first_sender_visible, True)
		self.assertEqual(msg.second_sender_visible, True)

		#Now we are gonna send another message to the same thread
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content2}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Message sent succesfully")
		#Then we are gonna check if the message has been sent...
		#Check if profile1 has 3 message and profile2 has 3 message as well...
		self.assertEqual(len(self.profile1.notifications_sender.all()) + len(self.profile1.notifications_receiver.all()), 3)
		self.assertEqual(len(self.profile2.notifications_sender.all()) + len(self.profile2.notifications_receiver.all()), 3)
		#Check if the newest message is the one we've just sended
		msg = Messages.objects.filter(reference = ref).order_by('created')[2]
		self.assertEqual(msg.private_message, content2)
		self.assertEqual(msg.reference, ref)

		#Now profile1 is gonna send another message to the same thread, so the sender timeline goes like this[prof1 --> prof2 --> prof1 --> prof1]
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content3}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Message sent succesfully")
		#Then we are gonna check if the message has been sent...
		#Check if profile1 has 4 message and profile2 has 4 message as well...
		self.assertEqual(len(self.profile1.notifications_sender.all()) + len(self.profile1.notifications_receiver.all()), 4)
		self.assertEqual(len(self.profile2.notifications_sender.all()) + len(self.profile2.notifications_receiver.all()), 4)
		#Check if the newest message is the one we've just sended
		msg = Messages.objects.filter(reference = ref).order_by('created')[3]
		self.assertEqual(msg.private_message, content3)
		self.assertEqual(msg.reference, ref)

		#You are not permitted to respond in a thread that is not yours
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref2, "data": {"content": content3}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "You are not permitted to respond in a thread that is not yours")

		#The message of the notification is too long
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content4}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The message of the notification is too long")

		#The message of the notification cannot be empty
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": ""}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The message of the notification cannot be empty")

		#The requested message does not exists
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": str(uuid.uuid4()), "data": {"content": "asd"}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The requested message does not exists")
	
	
	def test_post_request(self):
		#Initialize variables
		c = Client()
		content1 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content2 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content3 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content4 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(10000))

		#Create the wing related to the request
		wing = G(Accomodation, city= self.profile2.current_city, author= self.profile2)
		#Make a thread of requests
		ref = str(uuid.uuid4())
		created = time.time() - 3600*24
		check_created = created
		strt_date = 1357948800
		nd_date= 1358208000
		num_ppl = 1
		flex_start= False
		flex_end= False
		trans= 'Plane'
		total_msg = 1
		current_msg= 0
		#[P, P, X, X, X, P, A, A, A, M, M, M, P, X, P, A, M, X, P, A, M, D, D, D, M, D, A]
		#[1, 1, 1, 1, 2, 1, 2..]
		#Let's create our first request.
		#Now the request is in Pending. Profile 1 can Chat or Cancel. Profile2 can Accept, Maybe or Decline
		#######Pending-> p2 maybe, decline
		#Try profile1 Chat
		#ERRORS: Porfile1 can't Accept, Maybe, Pending. Profile2 can't Pending or Chat
		#ERRORS: Try prof1 Accept
		#ERRORS: Try prof1 Maybe
		#ERRORS: Try prof1 Pending
		#ERRORS: Try prof2 Pending
		#ERRORS: Try prof2 Chat
		#Try profile1 Cancel		
		#Now the request is canceled. Profile1 can now put it into Pending or Chat. Profile2 can only Chat...
		#Try profile1 Chat
		#Try profile2 Chat
		#ERRORS: Profile1 can't Accept, Maybe, Cancel. Profile2 can't Accept, Maybe, Decline or Pending
		#ERRORS: Try prof1 Accept
		#ERRORS: Try prof1 Maybe
		#ERRORS: Try prof1 Cancel
		#ERRORS: Try prof2 Accept
		#ERRORS: Try prof2 Maybe
		#ERRORS: Try prof2 Decline
		#ERRORS: Try prof2 Pending
		#Try profile1 Pending
		#Now we have the request in Pending again... 
		#Let's try to do something we can't, like Accept, Maybe, Pending
		#ERRORS: We already checked them
		#Try prof2 Accept
		#Now the request is accepted. Prof1 can Chat, Maybe and Cancel. Prof2 can Chat, Maybe and Decline
		##########Accepted->p2 maybe, decline
		#Try prof1 Chat
		#Try prof2 Chat
		#ERRORS: Profile1 can't Accept and Pending. Profile2 can't Accept and Pending
		#ERRORS: Prof1 Accept
		#ERRORS: Prof1 Pending
		#ERRORS: Prof2 Accept
		#ERRORS: Prof2 Pending
		#Try prof1 Maybe
		#Now, prof1 has put Maybe. This means prof2 could Decline and Chat. Prof1 could Pending, Chat and Cancel
		#Try prof1 Chat
		#Try prof2 Chat
		#ERRORS: Prof1 can't Accept. Prof2 can't Accept, Maybe or Pending
		#ERRORS: Prof1 Accept
		#ERRORS: Prof2 Accept
		#ERRORS: Prof2 Maybe
		#ERRORS: Prof2 Pending
		#Try prof1 Accept
		#Now its back to Accept! 
		#Try prof1 Cancel
		#Try prof1 Pending
		#try prof2 Accept
		#Try prof1 Maybe
		#Try prof1 Cancel
		#Try prof1 Pending
		#try prof2 Accept
		#Try prof1 Maybe
		#Try prof2 Decline
		#Now profile2 has Declined! Prof1 can only Chat and prof2 can Accept, Maybe, Chat
		#Try Prof1 Chat
		#try Prof2 Chat
		#ERRORS: Prof1 can't Accept, Maybe, Decline and Pending. Prof2 can't Cancel or Pending
		#ERRORS: Prof1 Accept
		#ERRORS: Prof1 Maybe
		#ERRORS: Prof1 Decline
		#ERRORS: Prof1 Pending
		#ERRORS: Prof2 Cancel
		#ERRORS: Prof2 Pending
		#Try prof2 Maybe
		#Try prof2 Decline
		#Try prof2 Accept
		#Back to Accepted!


		#Let's create our first request.
		request = G(Requests, reference = ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=created, private_message = content1, public_message= content2, wing= wing)
		additional_info= G(AccomodationInformation, notification=request, start_date=strt_date, end_date=nd_date, transport= trans, num_people= num_ppl)
		#Check if profile1 has 1 request and profile2 has 1 request as well...
		self.assertEqual(len(self.profile1.notifications_sender.all()) + len(self.profile1.notifications_receiver.all()), 1)###########################################
		self.assertEqual(len(self.profile2.notifications_sender.all()) + len(self.profile2.notifications_receiver.all()), 1)###########################################
		#Now the request is in Pending. Profile 1 can Chat or Cancel. Profile2 can Accept, Maybe or Decline
		#######Pending-> p2 maybe, decline
		#Try profile1 Chat
		time.sleep(1)
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		
		
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'P')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#ERRORS: Porfile1 can't Accept, Maybe,. Profile2 can't Pending or Chat
		#ERRORS: Try prof1 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Try prof1 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Try prof2 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		time.sleep(1)
		#Try profile1 Cancel
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		
		
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Now the request is canceled. Profile1 can now put it into Pending or Chat. Profile2 can only Chat...
		#Try profile1 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		
		
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		strt_date = strt_date
		time.sleep(1)
		#Try profile2 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#ERRORS: Profile1 can't Accept, Maybe, Cancel. Profile2 can't Accept, Maybe, Decline or Pending
		#ERRORS: Try prof1 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Try prof1 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Try prof2 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Try prof2 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Try prof2 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		time.sleep(1)
		#Try profile1 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		
		
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'P')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#Now we have the request in Pending again... 
		#Let's try to do something we can't, like Accept, Maybe, Pending
		#ERRORS: We already checked them
		time.sleep(1)
		#Try prof2 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		
		self.assertEqual(req.state, 'A')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#Now the request is accepted. Prof1 can Chat, Maybe and Cancel. Prof2 can Chat, Maybe and Decline
		##########Accepted->p2 maybe, decline
		time.sleep(1)
		#Try prof1 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'A')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof2 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'A')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#ERRORS: Profile1 can't Accept and Pending. Profile2 can't Accept and Pending
		#ERRORS: Prof1 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Prof2 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		time.sleep(1)
		#Try prof1 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'M')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#Now, prof1 has put Maybe. This means prof2 could Decline and Chat. Prof1 could Accept, Chat and Cancel
		time.sleep(1)
		#Try prof1 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		
		
		self.assertEqual(req.state, 'M')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof2 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		
		
		self.assertEqual(req.state, 'M')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#ERRORS: Prof1 can't Pending. Prof2 can't Pending
		#ERRORS: Prof2 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		time.sleep(1)
		#ERRORS: Prof1 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		time.sleep(1)
		#Check if it's OK
		#Try Prof1 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'A')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#Now its back to Pending! 
		time.sleep(1)
		#Try prof1 Cancel
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof1 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'P')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#try prof2 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'A')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof1 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'M')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof1 Cancel
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof1 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'P')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#try prof2 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'A')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof1 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'M')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof2 Decline
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Now profile2 has Declined! Prof1 can only Chat and prof2 can Accept, Maybe, Chat
		#Try Prof1 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile1.pk)
		self.assertEqual(req.receiver.pk, self.profile2.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#try Prof2 Chat
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		
		#ERRORS: Prof1 can't Accept, Maybe, Decline and Pending. Prof2 can't Cancel or Pending
		#ERRORS: Prof1 Accept
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "A", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Prof1 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Prof1 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		#ERRORS: Prof2 Pending
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "P", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], False)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 400)
		self.assertTrue(js.has_key('errors'))
		self.assertEqual(js['errors'], "The operation you requested is not valid")
		time.sleep(1)
		#Try prof2 Maybe
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "M", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'M')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Try prof2 Decline
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": "D", "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		total_msg = total_msg + 1
		current_msg = current_msg + 1
		#Check if it's OK
		req_list = Requests.objects.filter(reference= ref).order_by('created')
		self.assertEqual(len(req_list), total_msg) 
		req = req_list[current_msg]
		self.assertEqual(req.state, 'D')###############################################################
		self.assertEqual(req.sender.pk, self.profile2.pk)
		self.assertEqual(req.receiver.pk, self.profile1.pk)
		##
		self.assertEqual(req.public_message, "")
		self.assertEqual(req.private_message, content1) 
		self.assertEqual(req.make_public, False)
		##
		ai_list = AccomodationInformation.objects.filter(notification__pk= req.pk)
		self.assertEqual(len(ai_list), 1)
		ai = ai_list[0]
		self.assertEqual(ai.start_date, strt_date)
		self.assertEqual(ai.end_date, nd_date)
		self.assertEqual(ai.num_people, num_ppl)
		self.assertEqual(ai.flexible_start, flex_start)
		self.assertEqual(ai.flexible_end, flex_end)
		
		time.sleep(1)
		#Back to Accepted!

	def test_post_request_param_modification(self):
		c = Client()
		content1 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		content2 = ''.join(random.choice(string.letters + string.digits + string.whitespace) for x in range(200))
		#Create the wing related to the request
		wing = G(Accomodation, city= self.profile2.current_city, author= self.profile2)
		wing2 = G(Accomodation, city= self.profile2.current_city, author= self.profile2)
		#Make a thread of requests
		ref = str(uuid.uuid4())
		created = time.time() - 3600*24
		check_created = created
		strt_date = 1357948800
		nd_date= 1358208000
		num_ppl = 1
		flex_start= False
		flex_end= False
		trans= 'Plane'
		total_msg = 1
		current_msg= 0

		#Create the first request
		request = G(Requests, reference = ref, sender=self.profile1, receiver=self.profile2, first_sender=self.profile1, kind="request", created=created, private_message = content1, public_message= content2, wing= wing, state='P')
		additional_info= G(AccomodationInformation, notification=request, start_date=strt_date, end_date=nd_date, transport= trans, num_people= num_ppl)
		#Check if profile1 has 1 request and profile2 has 1 request as well...
		self.assertEqual(len(self.profile1.notifications_sender.all()) + len(self.profile1.notifications_receiver.all()), 1)
		self.assertEqual(len(self.profile2.notifications_sender.all()) + len(self.profile2.notifications_receiver.all()), 1)
		time.sleep(1)

		#Prof2 Accepts, but modifies end_date -> 1358160306
		nd_date = 1358160306
		mod = ['endDate']
		state = 'A'
		nmod = 1
		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		time.sleep(1)
		#Check the modifications are shown for prof1, but no modifications are shown for profile2
		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), nmod)
			for i in params['modified']:
				self.assertTrue(i in mod)	

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), 0)
			for i in params['modified']:
				self.assertTrue(i in mod)		

		#check also in the notification list, that changes are shown for prof1
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 1)
		self.assertEqual(json.loads(r1.content)['data']['count'], 1)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), 1)
		first = items[0]
		self.assertTrue(isinstance(first, dict))
		self.assertTrue(first.has_key('wingParameters'))
		params = first['wingParameters']
		self.assertTrue(isinstance(params, dict))
		self.assertTrue(params.has_key('modified'))
		self.assertTrue(params.has_key('wingType'))
		self.assertTrue(params.has_key('message'))
		self.assertTrue(params.has_key('endDate'))
		self.assertTrue(params.has_key('startDate'))
		self.assertTrue(params.has_key('numPeople'))
		self.assertTrue(params.has_key('wingCity'))
		self.assertTrue(isinstance(params['modified'], list))
		self.assertEqual(len(params['modified']), nmod)

		#Prof1 Accepts (Chats)
		nd_date = 1358160306
		mod = []
		state = 'A'
		nmod = 0

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		time.sleep(1)
		#Check the modifications are gone for prof1
		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), nmod)
			for i in params['modified']:
				self.assertTrue(i in mod)	

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), 0)
			for i in params['modified']:
				self.assertTrue(i in mod)		

		#check also in the notification list, that changes are gone for prof1
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 1)
		self.assertEqual(json.loads(r1.content)['data']['count'], 1)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), 1)
		first = items[0]
		self.assertTrue(isinstance(first, dict))
		self.assertTrue(first.has_key('wingParameters'))
		params = first['wingParameters']
		self.assertTrue(isinstance(params, dict))
		self.assertTrue(params.has_key('modified'))
		self.assertTrue(params.has_key('wingType'))
		self.assertTrue(params.has_key('message'))
		self.assertTrue(params.has_key('endDate'))
		self.assertTrue(params.has_key('startDate'))
		self.assertTrue(params.has_key('numPeople'))
		self.assertTrue(params.has_key('wingCity'))
		self.assertTrue(isinstance(params['modified'], list))
		self.assertEqual(len(params['modified']), nmod)

		#Prof1 Maybe and changes num_ppl -> 4
		nd_date = 1358160306
		num_ppl = 4
		mod = ['capacity']
		state = 'M'
		nmod = 1

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		time.sleep(1)
		#check prof1 does not see the modified values, but prof2 sees them
		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), nmod)
			for i in params['modified']:
				self.assertTrue(i in mod)	

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), 0)
			for i in params['modified']:
				self.assertTrue(i in mod)
		#check also in the notification list, that changes are shown for prof2
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 1)
		self.assertEqual(json.loads(r1.content)['data']['count'], 1)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), 1)
		first = items[0]
		self.assertTrue(isinstance(first, dict))
		self.assertTrue(first.has_key('wingParameters'))
		params = first['wingParameters']
		self.assertTrue(isinstance(params, dict))
		self.assertTrue(params.has_key('modified'))
		self.assertTrue(params.has_key('wingType'))
		self.assertTrue(params.has_key('message'))
		self.assertTrue(params.has_key('endDate'))
		self.assertTrue(params.has_key('startDate'))
		self.assertTrue(params.has_key('numPeople'))
		self.assertTrue(params.has_key('wingCity'))
		self.assertTrue(isinstance(params['modified'], list))
		self.assertEqual(len(params['modified']), nmod)
		#Prof2 Maybe
		nd_date = 1358160306
		num_ppl = 4
		mod = []
		state = 'M'
		nmod = 0

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		self.assertEqual(js['data'], "Request sent succesfully")
		time.sleep(1)
		#Check prof2 does not sees any changes
		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), nmod)
			for i in params['modified']:
				self.assertTrue(i in mod)	

		#Prof2 declines
		nd_date = 1358160306
		num_ppl = 4
		mod = []
		state = 'D'
		nmod = 0

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		time.sleep(1)
		#Prof2 Maybes, and changes num_ppl -> 3
		nd_date = 1358160306
		num_ppl = 3
		mod = ['capacity']
		state = 'M'
		nmod = 1

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		time.sleep(1)

		#Prof2 Maybes, and changes end_date -> 1358208000
		nd_date = 1358208000
		num_ppl = 3
		mod = ['capacity', 'endDate']
		state = 'M'
		nmod = 2

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		time.sleep(1)

		#Check Prof1 sees both changes
		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), nmod)
			for i in params['modified']:
				self.assertTrue(i in mod)	

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), 0)
			for i in params['modified']:
				self.assertTrue(i in mod)

		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 1)
		self.assertEqual(json.loads(r1.content)['data']['count'], 1)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), 1)
		first = items[0]
		self.assertTrue(isinstance(first, dict))
		self.assertTrue(first.has_key('wingParameters'))
		params = first['wingParameters']
		self.assertTrue(isinstance(params, dict))
		self.assertTrue(params.has_key('modified'))
		self.assertTrue(params.has_key('wingType'))
		self.assertTrue(params.has_key('message'))
		self.assertTrue(params.has_key('endDate'))
		self.assertTrue(params.has_key('startDate'))
		self.assertTrue(params.has_key('numPeople'))
		self.assertTrue(params.has_key('wingCity'))
		self.assertTrue(isinstance(params['modified'], list))
		self.assertEqual(len(params['modified']), nmod)

		#Prof1 Accepts and changes num_ppl -> 2
		nd_date = 1358208000
		num_ppl = 2
		mod = ['capacity']
		state = 'A'
		nmod = 1

		r1 = c.post('/api/v1/notificationsthread/', json.dumps({"reference": ref, "data": {"content": content1, "state": state, "wingParameters": {"startDate": strt_date, "endDate": nd_date, "capacity": num_ppl, "flexibleStartDate": flex_start, "flexibleEndDate": flex_end}}}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		time.sleep(1)

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), nmod)
			for i in params['modified']:
				self.assertTrue(i in mod)	

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(js['data'].has_key('wing'), True)
		self.assertTrue(isinstance(data['wing'], dict))
		wing_aux = data['wing']
		self.assertTrue(wing_aux.has_key('type'))
		self.assertEqual(wing_aux['type'], 'Accomodation')
		self.assertTrue(wing_aux.has_key('state'))
		self.assertEqual(wing_aux['state'], state)
		self.assertTrue(wing_aux.has_key('parameters'))
		self.assertTrue(isinstance(wing_aux['parameters'], dict))
		params = wing_aux['parameters']
		if (wing_aux['type'] == 'Accomodation'):
			self.assertTrue(params.has_key('wingId'))
			self.assertEqual(params['wingId'], wing.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], wing.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], wing.city.stringify())
			self.assertTrue(params.has_key('startDate'))
			self.assertEqual(params['startDate'], strt_date)
			self.assertTrue(params.has_key('endDate'))
			self.assertEqual(params['endDate'], nd_date)
			self.assertTrue(params.has_key('capacity'), num_ppl)
			self.assertTrue(params.has_key('arrivingVia'), trans)
			self.assertTrue(params.has_key('flexibleStartDate'), flex_start)
			self.assertTrue(params.has_key('flexibleEndDate'), flex_end)
			self.assertTrue(params.has_key('modified'))
			self.assertTrue(isinstance(params['modified'], list))
			self.assertEqual(len(params['modified']), 0)
			for i in params['modified']:
				self.assertTrue(i in mod)

		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 1)
		self.assertEqual(json.loads(r1.content)['data']['count'], 1)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), 1)
		first = items[0]
		self.assertTrue(isinstance(first, dict))
		self.assertTrue(first.has_key('wingParameters'))
		params = first['wingParameters']
		self.assertTrue(isinstance(params, dict))
		self.assertTrue(params.has_key('modified'))
		self.assertTrue(params.has_key('wingType'))
		self.assertTrue(params.has_key('message'))
		self.assertTrue(params.has_key('endDate'))
		self.assertTrue(params.has_key('startDate'))
		self.assertTrue(params.has_key('numPeople'))
		self.assertTrue(params.has_key('wingCity'))
		self.assertTrue(isinstance(params['modified'], list))
		self.assertEqual(len(params['modified']), nmod)

class AutomataTest(TestCase):
	def setUp(self):
		self.profile1 = G(UserProfile, pk=1)
		#make some users and profiles as example
		self.sample1 = [['P', 1],['A', 2],['A', 1],['D', 1],['D', 2],['P', 1],['A', 2],['A', 2],['M', 1],['M', 1],['M', 2],['D', 2],['D', 1],['D', 2],['M', 2],['D', 1],['D', 1],['D', 2],['P', 1],['D', 2],['D', 2],['A', 2],['M', 2],['M', 2],['D', 2],['A', 2],['M', 1],['A', 1],['M', 1],['D', 1]]
		self.sample2 = [['P', 1],['A', 2],['A', 1],['D', 1],['D', 2],['P', 1],['A', 2],['A', 2],['M', 1],['M', 1],['M', 2],['D', 2],['D', 1],['D', 2],['M', 2],['D', 1],['D', 1],['D', 2],['M', 1]]

	def test_post_message(self):
		a = Automata()
		self.assertTrue(a.check_P(self.sample1, self.profile1))
		self.assertFalse(a.check_P(self.sample2, self.profile1))

class NumberNotifsTest(TestCase):
	def setUp(self):
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token		

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

	def test_receive_n_notifs(self):
		c = Client()
		#Start looking for 0 notis
		r1 = c.get('/api/v1/notificationslist/', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 0)
		#p2 adds 1 notif with p1 as a receiver. notifs-> 1
		ref = uuid.uuid4()
		notif1 = G(Messages, sender=self.profile2, receiver = self.profile1, reference= str(ref))
		r1 = c.get('/api/v1/notificationslist/', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 1)
		#p2 adds 1 more notif in the same thread -> 1
		notif1 = G(Messages, sender=self.profile2, receiver = self.profile1, reference= str(ref))
		r1 = c.get('/api/v1/notificationslist/', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 1)
		#p1 reads the thread-> 0
		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 0)
		#p2 adds 1 notif -> 1
		notif1 = G(Messages, sender=self.profile2, receiver = self.profile1, reference= str(ref))
		r1 = c.get('/api/v1/notificationslist/', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 1)
		#p2 adds another notif, different thread -> 2
		ref2 = uuid.uuid4()
		notif1 = G(Messages, sender=self.profile2, receiver = self.profile1, reference= str(ref2))
		r1 = c.get('/api/v1/notificationslist/', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 2)
		#p1 reads the second -> 1
		r1 = c.get('/api/v1/notificationsthread/' + str(ref2), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(json.loads(r1.content)['code'], 200)
		self.assertTrue(isinstance(json.loads(r1.content)['updates'], dict))
		self.assertTrue(json.loads(r1.content)['updates'].has_key('notifs'))
		self.assertEqual(json.loads(r1.content)['updates']['notifs'], 1)

