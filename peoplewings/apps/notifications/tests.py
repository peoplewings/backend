"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import datetime
from django.test import Client
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.notifications.models import Notifications
from django.contrib.auth.models import User
from django.utils.timezone import utc
 
class PaginationTest(TestCase):
 
	def setUp(self):
		self.hadeer = User.objects.create_user(username = 'a@a.com', password = '123456')
		self.ph = UserProfile.objects.create(user = self.hadeer)

		self.john = User.objects.create_user(username = 'b@b.com', password = '123456')
		self.pj = UserProfile.objects.create(user = self.john)

		self.n1 = Notifications.objects.create(sender = self.pj, receiver = self.ph, reference="1")
		self.n2 = Notifications.objects.create(sender = self.ph, receiver = self.pj, reference="1")

		self.n3 = Notifications.objects.create(sender = self.ph, receiver = self.pj, reference="2")
		self.n4 = Notifications.objects.create(sender = self.ph, receiver = self.pj, reference="2")
		self.n5 = Notifications.objects.create(sender = self.pj, receiver = self.ph, reference="2")

 
	def test_models(self):
		self.assertEqual(Notifications.objects.filter(receiver=self.pj).count(), 3)
		self.assertEqual(Notifications.objects.filter(sender=self.ph).count(), 3)

		self.assertEqual(Notifications.objects.filter(sender=self.pj).count(), 2)
		self.assertEqual(Notifications.objects.filter(receiver=self.ph).count(), 2)

	def test_not_logged_in(self):
		c = Client()
		response = c.get('/api/v1/notificationslist?kind=reqinv', content_type='application/json')

		self.assertEqual(response.status_code, 401)
 
	def test_logged_in(self):
		c = Client()
		import json
		#c.login(username='Hadeer', password='123456')
		response = c.post('/api/v1/auth', json.dumps({ 'username' : 'a@a.com', 'password' : '123456'}), content_type='application/json')
		token = json.loads(response.content)['data']['xAuthToken']		
		response = c.get('/api/v1/notificationslist?kind=reqinv', HTTP_X_AUTH_TOKEN=token, content_type='application/json')

		self.assertEqual(response.status_code, 200)