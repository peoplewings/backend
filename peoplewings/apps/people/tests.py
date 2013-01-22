import string
import random
import json
from datetime import datetime
import uuid
import time

from django.test import TestCase, Client
from django_dynamic_fixture import G, get, F
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from people.models import UserProfile, University
from peoplewings.libs.customauth.models import ApiToken

from django.utils.timezone import utc

class UniversitiesTest(TestCase):

	def setUp(self):
		#make some users and profiles as example
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		
		self.uni1 = G(University, name='Universitat Politecnica de Catalunya')
		self.uni2 = G(University, name='Universitat Politecnica de Madrid')
		self.uni3 = G(University, name='Universitat de Barcelona')
		self.uni4 = G(University, name='Universitat Internacional de Catalunya')
		self.uni5 = G(University, name='ESADE')
		self.uni6 = G(University, name='Universitat Rovira i Virgili')
		self.uni7 = G(University, name='Dean College')
		self.uni8 = G(University, name='Universidad complutense de Madrid')
		self.uni9 = G(University, name='Harvard University')
		self.uni10 = G(University, name='Princenton College')


	def get_universities_success(self, result, **kwargs):
		self.assertEqual(result.status_code, 200)
		js = json.loads(result.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		self.assertTrue(js.has_key('code'))
		self.assertEqual(js['code'], 200)
		self.assertTrue(js.has_key('data'))
		data = js['data']
		self.assertTrue(isinstance(data, list))
		self.assertEqual(len(data), kwargs['count'])
		for i in data:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key("name"))
			self.assertTrue(i['name'] in [j['name'] for j in kwargs['expected']])

	def test_get_universities(self):
		#Initialize variables
		c = Client()
		name = ''
		expected = []
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=0, expected = expected)
		#check with ESA. 1 result...
		name = 'ESA'
		expected = [{"name":"ESADE"}]
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=1, expected = expected)
		#check with esa. 1 result...
		name = 'esa'
		expected = [{"name":"ESADE"}]
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=1, expected = expected)
		#check with universitat. 5 results
		name = 'universitat'
		expected = [{"name":"Universitat Politecnica de Catalunya"},{"name":'Universitat Politecnica de Madrid'},{"name":"Universitat de Barcelona"},{"name":"Universitat Internacional de Catalunya"},{"name":"Universitat Rovira i Virgili"}]
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=5, expected = expected)
		#check with universi. 5 results (pagination works!)
		name = 'universi'
		expected = [{"name":"Universitat Politecnica de Catalunya"},{"name":'Universitat Politecnica de Madrid'},{"name":"Universitat de Barcelona"},{"name":"Universitat Internacional de Catalunya"},{"name":"Universitat Rovira i Virgili"}]
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=5, expected = expected)
		#check with colleg. 2 result
		name = 'colleg'
		expected = [{"name":'Dean College'},{"name":"Princenton College"}]
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=2, expected = expected)
		#check with zorra. 0 results
		name = 'zorra'
		expected = []
		r1 = c.get('/api/v1/universities/?name=%s' % name, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.get_universities_success(r1, count=0, expected = expected)
