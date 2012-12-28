"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from datetime import datetime
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.notifications.models import Notifications, Messages
from django.contrib.auth.models import User
from django.utils.timezone import utc
import json
 
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
		






