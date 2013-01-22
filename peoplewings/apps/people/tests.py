import string
import random
import json
import uuid
import time

from datetime import datetime
from django.utils.timezone import utc

from django.test import TestCase, Client
from django_dynamic_fixture import G, get, F
from django.core.urlresolvers import reverse
from people.models import UserProfile
from notifications.models import Notifications, Requests, Invites, Messages
from wings.models import Wing
from peoplewings.libs.customauth.models import ApiToken

 
class ContactsTest(TestCase):
	
	def setUp(self):
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
 
	def test_get_shortwings(self):
		c = Client()
		#user1 wants to get his contact list 0 => 0 contacts
		r = c.get('/api/v1/contacts', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('code'))
		self.assertEqual(content['code'], 200)
		self.assertTrue(content.has_key('msg'))
		self.assertEqual(content['msg'], "Candidates retrieved successfully")
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 0)

		#We add some contacts to user1...
		self.profile2 = G(UserProfile, user=F(first_name='Aaron', last_name= 'Guerrero'))
		self.profile3 = G(UserProfile, user=F(first_name='Montserrat', last_name= 'Tena'))
		self.profile4 = G(UserProfile, user=F(first_name='Zacarias', last_name= 'Guerrero'))
		self.profile5 = G(UserProfile, user=F(first_name='Montserrat', last_name= 'Caballe'))

		self.notification1 = G(Messages, sender= self.profile1, receiver= self.profile2)
		self.notification2 = G(Messages, sender= self.profile3, receiver= self.profile1)
		self.notification3 = G(Requests, sender= self.profile1, receiver= self.profile4, wing=F(author=self.profile4))
		self.notification4 = G(Invites, sender= self.profile5, receiver= self.profile1, wing=F(author=self.profile5))

		#If then, we make the same call, we should obtain => 	4 contacts
		r = c.get('/api/v1/contacts', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('code'))
		self.assertEqual(content['code'], 200)
		self.assertTrue(content.has_key('msg'))
		self.assertEqual(content['msg'], "Candidates retrieved successfully")
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 4)

		#We check then, if they are ordered by name... the order should be 0 => prof2, prof5, prof3, prof4
		aux = l1[0]
		self.assertTrue(aux.has_key('name'))
		self.assertEqual(aux['name'], self.profile2.user.first_name)
		self.assertTrue(aux.has_key('lastName'))
		self.assertEqual(aux['lastName'], self.profile2.user.last_name)
		self.assertTrue(aux.has_key('id'))
		self.assertEqual(aux['id'], self.profile2.pk)
		aux = l1[1]
		self.assertTrue(aux.has_key('name'))
		self.assertEqual(aux['name'], self.profile5.user.first_name)
		self.assertTrue(aux.has_key('lastName'))
		self.assertEqual(aux['lastName'], self.profile5.user.last_name)
		self.assertTrue(aux.has_key('id'))
		self.assertEqual(aux['id'], self.profile5.pk)
		aux = l1[2]
		self.assertTrue(aux.has_key('name'))
		self.assertEqual(aux['name'], self.profile3.user.first_name)
		self.assertTrue(aux.has_key('lastName'))
		self.assertEqual(aux['lastName'], self.profile3.user.last_name)
		self.assertTrue(aux.has_key('id'))
		self.assertEqual(aux['id'], self.profile3.pk)
		aux = l1[3]
		self.assertTrue(aux.has_key('name'))
		self.assertEqual(aux['name'], self.profile4.user.first_name)
		self.assertTrue(aux.has_key('lastName'))
		self.assertEqual(aux['lastName'], self.profile4.user.last_name)
		self.assertTrue(aux.has_key('id'))
		self.assertEqual(aux['id'], self.profile4.pk)

		#If we make the same call with type=request we should obtain only 2 contacts
		r = c.get('/api/v1/contacts?type=request', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('code'))
		self.assertEqual(content['code'], 200)
		self.assertTrue(content.has_key('msg'))
		self.assertEqual(content['msg'], "Candidates retrieved successfully")
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 2)

		#We check then, if they are ordered by name... the order should be 0 => prof5, prof4
		aux = l1[0]
		self.assertTrue(aux.has_key('name'))
		self.assertEqual(aux['name'], self.profile5.user.first_name)
		self.assertTrue(aux.has_key('lastName'))
		self.assertEqual(aux['lastName'], self.profile5.user.last_name)
		self.assertTrue(aux.has_key('id'))
		self.assertEqual(aux['id'], self.profile5.pk)
		aux = l1[1]
		self.assertTrue(aux.has_key('name'))
		self.assertEqual(aux['name'], self.profile4.user.first_name)
		self.assertTrue(aux.has_key('lastName'))
		self.assertEqual(aux['lastName'], self.profile4.user.last_name)
		self.assertTrue(aux.has_key('id'))
		self.assertEqual(aux['id'], self.profile4.pk)

		#if we make the call with a wrong GET paramter, is ignored, and the call is the same as with no params
		r = c.get('/api/v1/contacts?puta=zorra', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('code'))
		self.assertEqual(content['code'], 200)
		self.assertTrue(content.has_key('msg'))
		self.assertEqual(content['msg'], "Candidates retrieved successfully")
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 4)


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
