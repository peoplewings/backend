import string
import random
import json
import uuid
import time

from datetime import datetime, timedelta
from django.utils.timezone import utc

from django.test import TestCase, Client
from django_dynamic_fixture import G, get, F
from django.core.urlresolvers import reverse

from peoplewings.libs.customauth.models import ApiToken
from wings.models import Accomodation
from people.models import UserProfile
from django.contrib.auth.models import User
from notifications.models import Requests, Invites, AccomodationInformation
from django.contrib.auth.hashers import make_password

 
class DeleteAccountTest(TestCase):
	
	def setUp(self):
		self.profile1 = G(UserProfile, birthday=datetime.strptime('01-01-1985', '%d-%m-%Y'), gender= 'Male', user=G(User, email='lol@lol.lol', password=make_password('asdf')))
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token

		self.profile2 = G(UserProfile, birthday=datetime.strptime('01-01-1985', '%d-%m-%Y'), gender= 'Male', user=G(User, email='kek@lol.lol', password=make_password('asdf')))
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
		self.profile3 = G(UserProfile, birthday = '1985-09-12', gender= 'Male')
		self.profile4 = G(UserProfile, birthday = '1985-09-12', gender= 'Male')

		self.wing1 = G(Accomodation, author=self.profile1)
		self.wing2 = G(Accomodation, author=self.profile2)
		self.wing3 = G(Accomodation, author=self.profile3)
		self.wing4 = G(Accomodation, author=self.profile4)

		self.created = 1357548600
		self.req_1_2 = G(Requests, receiver= self.profile2, sender = self.profile1, first_sender= self.profile1, wing=self.wing2, created=self.created)
		self.req_1_3 = G(Invites, receiver= self.profile3, sender = self.profile1, first_sender= self.profile1, wing=self.wing1)
		self.req_4_1 = G(Invites, receiver= self.profile1, sender = self.profile4, first_sender= self.profile4, wing=self.wing4)
 
	def test_login(self):
		c = Client()
		#Check if we can log in with the user...
		response = c.post('/api/v1/auth', json.dumps({ 'username' : 'lol@lol.lol', 'password' : 'asdf'}), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		#Delete an account and try to login
		response = c.post('/api/v1/accounts/', json.dumps({ 'currentPassword': 'asdf'}), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)

	def test_preview_profile(self):
		c = Client()
		#check if we can see the profile of another person
		response = c.get('/api/v1/profiles/%s/preview' % (self.profile2.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		response = c.get('/api/v1/profiles/%s/accomodations/preview' % (self.profile2.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		#Delete account
		response = c.post('/api/v1/accounts/', json.dumps({ 'currentPassword': 'asdf'}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		#Check if we can see the same profile
		response = c.get('/api/v1/profiles/%s/preview' % (self.profile2.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], False)
		response = c.get('/api/v1/profiles/%s/accomodations/preview' % (self.profile2.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)

	def test_search(self):
		c = Client()
		#check that the search gives us 4 results..
		c_count = 4
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=all&type=Host&gender=Both&startDate=2013-03-06&page=1', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))		
		data = content['data']
		self.assertTrue(isinstance(data, dict))
		self.assertTrue(data.has_key('count'))
		self.assertEqual(data['count'], c_count)
		self.assertTrue(data.has_key('endResult'))
		self.assertEqual(data['endResult'], c_count)
		#Delete a user
		response = c.post('/api/v1/accounts/', json.dumps({ 'currentPassword': 'asdf'}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		#Now the results should have gone down by 1...
		c_count = 3
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=all&type=Host&gender=Both&startDate=2013-03-06&page=1', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))		
		data = content['data']
		self.assertTrue(isinstance(data, dict))
		self.assertTrue(data.has_key('count'))
		self.assertEqual(data['count'], c_count)
		self.assertTrue(data.has_key('endResult'))
		self.assertEqual(data['endResult'], c_count)

	def test_notifications(self):
		c = Client()
		#Get all notifications
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), 3)
		self.assertEqual(json.loads(r1.content)['data']['count'], 3)
		#Delete an account
		response = c.post('/api/v1/accounts/', json.dumps({ 'currentPassword': 'asdf'}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		#Get all notifications
		c_count = 3
		r1 = c.get('/api/v1/notificationslist', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)
		self.assertEqual(len(json.loads(r1.content)['data']['items']), c_count)
		self.assertEqual(json.loads(r1.content)['data']['count'], c_count)
		items = json.loads(r1.content)['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertEqual(len(items), c_count)
		for i in items:
			first = i
			self.assertTrue(isinstance(first, dict))
			self.assertTrue(first.has_key('wingParameters'))
			params = first['wingParameters']
			self.assertTrue(first.has_key('interlocutorId'))
			if first['interlocutorId'] == "":
				self.assertEqual(first['interlocutorId'], "")
				self.assertTrue(first.has_key('age'))
				self.assertEqual(first['age'], "")
				self.assertTrue(first.has_key('avatar'))
				self.assertEqual(first['avatar'], "http://peoplewings-test-media.s3.amazonaws.com/thumb-blank_avatar.jpg")
				self.assertTrue(first.has_key('online'))
				self.assertEqual(first['online'], "F")
				self.assertTrue(first.has_key('created'))
				self.assertNotEqual(first['created'], "")
				self.assertTrue(first.has_key('flagDirection'))
				self.assertNotEqual(first['flagDirection'], "")
				self.assertTrue(first.has_key('id'))
				self.assertNotEqual(first['id'], "")
				self.assertTrue(first.has_key('kind'))
				self.assertNotEqual(first['kind'], "")
				self.assertTrue(first.has_key('location'))
				self.assertEqual(first['location'], "")
				self.assertTrue(first.has_key('name'))
				self.assertEqual(first['name'], "Unknown User")
				self.assertTrue(first.has_key('read'))
				self.assertNotEqual(first['read'], "")
				self.assertTrue(first.has_key('state'))
				self.assertNotEqual(first['state'], "")
				self.assertTrue(first.has_key('reference'))
				self.assertNotEqual(first['reference'], "")
				self.assertTrue(first.has_key('verified'))
				self.assertEqual(first['verified'], "")
				self.assertTrue(first.has_key('wingParameters'))
				wingParams= first['wingParameters']
				self.assertTrue(wingParams.has_key('wingType'))
				self.assertNotEqual(wingParams['wingType'], "")
				self.assertTrue(wingParams.has_key('endDate'))
				self.assertNotEqual(wingParams['endDate'], "")
				self.assertTrue(wingParams.has_key('startDate'))
				self.assertNotEqual(wingParams['startDate'], "")
				self.assertTrue(wingParams.has_key('numPeople'))
				self.assertNotEqual(wingParams['numPeople'], "")
				self.assertTrue(wingParams.has_key('message'))
				self.assertEqual(wingParams['message'], "Deleted Wing")
			else:

				self.assertNotEqual(first['interlocutorId'], "")
				self.assertTrue(first.has_key('age'))
				self.assertNotEqual(first['age'], "")
				self.assertTrue(first.has_key('avatar'))
				#self.assertEqual(first['avatar'], "https://peoplewings-test-media.s3.amazonaws.com/thumb-blank_avatar.jpg")
				self.assertTrue(first.has_key('online'))
				self.assertNotEqual(first['online'], "")
				self.assertTrue(first.has_key('created'))
				self.assertNotEqual(first['created'], "")
				self.assertTrue(first.has_key('flagDirection'))
				self.assertNotEqual(first['flagDirection'], "")
				self.assertTrue(first.has_key('id'))
				self.assertNotEqual(first['id'], "")
				self.assertTrue(first.has_key('kind'))
				self.assertNotEqual(first['kind'], "")
				self.assertTrue(first.has_key('location'))
				self.assertNotEqual(first['location'], "")
				self.assertTrue(first.has_key('name'))
				self.assertNotEqual(first['name'], "User of Peoplewings")
				self.assertTrue(first.has_key('read'))
				self.assertNotEqual(first['read'], "")
				self.assertTrue(first.has_key('state'))
				self.assertNotEqual(first['state'], "")
				self.assertTrue(first.has_key('reference'))
				self.assertNotEqual(first['reference'], "")
				self.assertTrue(first.has_key('verified'))
				self.assertNotEqual(first['verified'], "")
				self.assertTrue(first.has_key('wingParameters'))
				wingParams = first['wingParameters']
				self.assertTrue(wingParams.has_key('wingType'))
				self.assertNotEqual(wingParams['wingType'], "")
				self.assertTrue(wingParams.has_key('endDate'))
				self.assertNotEqual(wingParams['endDate'], "")
				self.assertTrue(wingParams.has_key('startDate'))
				self.assertNotEqual(wingParams['startDate'], "")
				self.assertTrue(wingParams.has_key('numPeople'))
				self.assertNotEqual(wingParams['numPeople'], "")
				self.assertTrue(wingParams.has_key('message'))
				#self.assertNotEqual(wingParams['message'], "Wing Deleted")

	def test_threads(self):
		c = Client()
		strt_date = 1357948600
		nd_date= 1358207900
		num_ppl = 1
		trans = "Plane"
		ref = self.req_1_2.reference
		G(AccomodationInformation, notification=self.req_1_2, start_date=strt_date, end_date=nd_date, transport= trans, num_people= num_ppl)
		strt_date = 1357948800
		nd_date= 1358208000
		req_1_2_2 = G(Requests, receiver= self.profile1, sender = self.profile2, first_sender= self.profile1, wing=self.wing2, reference = ref, created = self.created + 1000)
		G(AccomodationInformation, notification=req_1_2_2, start_date=strt_date, end_date=nd_date, transport= trans, num_people= num_ppl)
		strt_date = 1357948900
		nd_date= 1358208900
		req_1_2_3 = G(Requests, receiver= self.profile2, sender = self.profile1, first_sender= self.profile1, wing=self.wing2, reference = ref, created = self.created + 2000)
		G(AccomodationInformation, notification=req_1_2_3, start_date=strt_date, end_date=nd_date, transport= trans, num_people= num_ppl)
		strt_date = 1357949800
		nd_date= 1358209000
		req_1_2_4 = G(Requests, receiver= self.profile1, sender = self.profile2, first_sender= self.profile1, wing=self.wing2, reference = ref, created = self.created + 3000)
		G(AccomodationInformation, notification=req_1_2_4, start_date=strt_date, end_date=nd_date, transport= trans, num_people= num_ppl)

		#Get the notification thread...
		c = Client()

		r1 = c.get('/api/v1/notificationsthread/' + str(ref), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')		
		self.assertEqual(r1.status_code, 200)
		js = json.loads(r1.content)
		self.assertTrue(js.has_key('status'))
		self.assertEqual(js['status'], True)
		#Now let's check out the data we've just received...
		#... we know that the notifications come ordered from older to newer (ASC)
		self.assertEqual(js.has_key('data'), True)
		data = js['data']
		self.assertTrue(isinstance(data, dict))
		self.assertEqual(data.has_key('reference'), True)
		self.assertEqual(data['reference'], ref)
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
			self.assertEqual(params['wingId'], self.wing2.pk)
			self.assertTrue(params.has_key('wingName'))
			self.assertEqual(params['wingName'], self.wing2.name)
			self.assertTrue(params.has_key('wingCity'))
			self.assertEqual(params['wingCity'], self.wing2.city.name)
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
		self.assertEqual(len(data['items']), 4)		

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
			self.assertTrue(i.has_key('senderOnline'))
			self.assertTrue(i.has_key('receiverId'))
			self.assertEqual(i['receiverId'], expected_receiver.pk)
			self.assertTrue(i.has_key('receiverAvatar'))
			self.assertEqual(i['receiverAvatar'], expected_receiver.thumb_avatar)
			self.assertTrue(i.has_key('content'))
			self.assertTrue(i['content'].has_key('message'))

			rec = expected_sender
			expected_sender = expected_receiver
			expected_receiver = rec

	def test_find_contacts(self):
		c = Client()
		#Find the "friends" of user 1...
		r1 = c.get('/api/v1/contacts?type=message', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		items = content['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertTrue(len(items), 3)
		#Delete a user
		response = c.post('/api/v1/accounts/', json.dumps({ 'currentPassword': 'asdf'}), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		#See if the firend list has gone down by 1
		r1 = c.get('/api/v1/contacts?type=message', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		items = content['data']['items']
		self.assertTrue(isinstance(items, list))
		self.assertTrue(len(items),2)






