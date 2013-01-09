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
from django_dynamic_fixture import G, get
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.notifications.models import Notifications, Messages
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
		self.wing2 = G(Accomodation, author=self.profile2)

	def test_post_requests(self):
		c = Client()
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
		






