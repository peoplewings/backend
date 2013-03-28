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
from wings.models import Accomodation, Wing, PublicRequestWing
from locations.models import City
from django.contrib.auth.models import User
from people.models import UserProfile
from peoplewings.libs.customauth.models import ApiToken

from django.utils.timezone import utc

class CropTest(TestCase):
	def setUp(self):
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
		self.profile2 = G(UserProfile, user=G(User, first_name= 'Macho'))

	def test_get(self):
		c = Client()
		r1 = c.post('/api/v1/cropped', json.dumps({"img":"https://s3-eu-west-1.amazonaws.com/peoplewings-test-media/photos/4d3a3d232ac84514a990c2efb10208f2.png", "x":"40", "y": "40", "w":"160", "h":"160"}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)

