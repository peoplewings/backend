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
from django_dynamic_fixture import G, get
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.notifications.models import Notifications, Messages, Requests, Invites
from wings.models import Accomodation, Wing
from django.contrib.auth.models import User
from people.models import UserProfile
from peoplewings.libs.customauth.models import ApiToken

from django.utils.timezone import utc

 
class PaginationTest(TestCase):
	fixtures = ['locations.json', 'user.json', 'people.json', 'wings.json']

	
	def setUp(self):
		'''
		self.hadeer = User.objects.create_user(username = 'a@a.com', password = '123456')
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
		self.assertEqual(json.loads(r1.content)['data']['endResult'], 2)
		self.assertEqual(json.loads(r1.content)['data']['startResult'], 1)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 2)
		l1 = json.loads(r1.content)['data']['items']

		#check that not providing the page parameter has the same effect as calling with page=1
		r2 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r2.content)['code'], 200)
		self.assertEqual(json.loads(r2.content)['msg'], "OK")
		self.assertEqual(json.loads(r2.content)['status'], True)
		self.assertEqual(json.loads(r2.content)['data']['count'], 5)
		self.assertEqual(json.loads(r2.content)['data']['endResult'], 2)
		self.assertEqual(json.loads(r2.content)['data']['startResult'], 1)
		self.assertEqual(len(json.loads(r2.content)['data']['items']), 2)
		l2 = json.loads(r2.content)['data']['items']
		self.assertEqual(l1, l2)

		#check last page
		r4 = c.get('/api/v1/notificationslist?page=3', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r4.content)['code'], 200)
		self.assertEqual(json.loads(r4.content)['msg'], "OK")
		self.assertEqual(json.loads(r4.content)['status'], True)
		self.assertEqual(json.loads(r4.content)['data']['count'], 5)
		self.assertEqual(json.loads(r4.content)['data']['endResult'], 5)
		self.assertEqual(json.loads(r4.content)['data']['startResult'], 5)
		self.assertEqual(len(json.loads(r4.content)['data']['items']), 1)

		# checking unexisting pages...
		r3 = c.get('/api/v1/notificationslist?page=4', HTTP_X_AUTH_TOKEN=token, content_type='application/json')
		self.assertEqual(json.loads(r3.content)['code'], 413)
		self.assertEqual(json.loads(r3.content)['msg'], "Sorry, no results on that page.")
		self.assertEqual(json.loads(r3.content)['status'], False)

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
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 2)
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
		self.assertEqual(isinstance(js['data'], list), True)				
		for i in js['data']:			
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
			self.assertTrue(i.has_key('kind'))
			self.assertEqual(i['kind'], 'message')
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))
			self.assertTrue(i.has_key('created'))		
			self.assertEqual(i['created'], int(self.check_created))
			self.assertTrue(i.has_key('content'))
			self.assertEqual(i['reference'], self.ref)
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
