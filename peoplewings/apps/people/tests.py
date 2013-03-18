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
from people.models import UserProfile, University, Language, UserLanguage
from locations.models import City, Region, Country
from notifications.models import Notifications, Requests, Invites, Messages
from wings.models import Wing, Accomodation, PublicRequestWing
from peoplewings.libs.customauth.models import ApiToken
import threading
from django.contrib.auth.models import User

 
class ContactsTest(TestCase):
	
	def setUp(self):
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
 
	def test_get_shortwings(self):
		c = Client()
		#user1 wants to get his contact list 0 => 0 contacts
		r = c.get('/api/v1/contacts', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')	
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
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
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
		
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

class UserAndProfileSameIdTest(TestCase):

	def setUp(self):
		pass

	def test_register(self):
		c = Client()
		email = str(random.getrandbits(10))
		r1 = c.post('/api/v1/newuser', json.dumps({"birthdayDay":5, "birthdayMonth":3, "birthdayYear":1999, "email":"%s@peoplewings.com" % email, "repeatEmail":"%s@peoplewings.com" % email, "firstName":"Ez", "gender":"Male", "lastName":"Pz", "password":"asdfasdf01?", "hasAcceptedTerms": True}), content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(json.loads(r1.content)['status'], True)

class ReplyRateorTimeTest(TestCase):

	def setUp(self):
		self.profile1 = G(UserProfile, birthday = '1985-09-12')
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
		self.wing1 = G(Accomodation, author=self.profile1, capacity=1, )

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token

	def test_profiles_detail(self):
		c = Client()
		r1 = c.get('/api/v1/profiles/%s' % self.profile1.pk, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		data = content['data']
		self.assertTrue(data.has_key('replyRate'))
		self.assertTrue(data.has_key('replyTime'))
		self.assertEqual(data['replyRate'], 0)
		self.assertEqual(data['replyTime'], 0)

class SearchFineTest(TestCase):

	def setUp(self):
		self.lang1 = G(Language, name= 'english')
		self.lang2 = G(Language, name= 'spanish')
		self.lang3 = G(Language, name= 'french')
		self.lang4 = G(Language, name= 'catalan')
		self.lang5 = G(Language, name= 'japanese')

		self.city1 = G(City, name='Barcelona')
		self.city2 = G(City, name='Tokyo')
		self.city3 = G(City, name='Tolouse')
		self.city4 = G(City, name='London')
		self.city5 = G(City, name='Fachadolid')

		self.profile1 = G(UserProfile, birthday = '1985-09-12', gender= 'Male') ## 27 ays
		self.lang1_1 = G(UserLanguage, user_profile= self.profile1, language=self.lang1)
		self.wing1 = G(Accomodation, author=self.profile1, capacity=1, date_start=None, date_end=None, city=self.city4)		

		self.profile2 = G(UserProfile, birthday = '1981-09-12', gender= 'Female') ## 31 anys
		self.lang2_1 = G(UserLanguage, user_profile= self.profile2, language=self.lang2)
		self.wing2 = G(Accomodation, author=self.profile2, capacity=2, date_start=None, date_end=None, city=self.city5)

		self.profile3 = G(UserProfile, birthday = '1989-09-12', gender= 'Male') ## 23 anys
		self.lang3_1 = G(UserLanguage, user_profile= self.profile3, language=self.lang3)
		self.wing3 = G(Accomodation, author=self.profile3, capacity=3, date_start=None, date_end=None, city=self.city3)

		self.profile4 = G(UserProfile, birthday = '1965-09-12', gender= 'Female') ##47 anys
		self.lang4_1 = G(UserLanguage, user_profile= self.profile4, language=self.lang4)
		self.wing4 = G(Accomodation, author=self.profile4, capacity=4, date_start=None, date_end=None, city=self.city1)

		self.profile5 = G(UserProfile, birthday = '1975-09-12', gender= 'Male') ## 37 anys
		self.lang5_1 = G(UserLanguage, user_profile= self.profile5, language=self.lang5)
		self.wing5 = G(Accomodation, author=self.profile5, capacity=5, date_start='2013-04-01', date_end=None, city=self.city2)

	def test_search_filtering(self):
		c = Client()
		token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
		c_count= 4
		# Basci search, we dont check the sorting yet...
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=all&type=Host&gender=Both&startDate=2013-03-15&page=1', HTTP_X_AUTH_TOKEN=token1, content_type='application/json')
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
		self.assertTrue(data.has_key('profiles'))
		profiles = data['profiles']
		self.assertTrue(isinstance(profiles, list))
		self.assertEqual(len(profiles), c_count)
		for i in profiles:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('age'))
			self.assertTrue(i.has_key('allAboutYou'))
			self.assertTrue(i.has_key('avatar'))
			self.assertTrue(i.has_key('current'))
			self.assertTrue(isinstance(i['current'], dict))
			self.assertTrue(i.has_key('firstName'))
			self.assertTrue(i.has_key('lastName'))
			self.assertTrue(i.has_key('languages'))
			self.assertTrue(isinstance(i['languages'], list))
			self.assertTrue(i.has_key('online'))
			self.assertTrue(i.has_key('replyRate'))
			self.assertTrue(i.has_key('replyTime'))
			self.assertTrue(i.has_key('profileId'))
			self.assertTrue(i.has_key('dateJoined'))
			#Check if the values are correct....
			aux_prof = UserProfile.objects.filter(pk=i['profileId'])
			self.assertEqual(len(aux_prof), 1)

		# More basics. This time we only select english speakers
		c_count = 1
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=english&type=Host&gender=Both&startDate=2013-03-15&page=1', HTTP_X_AUTH_TOKEN=token1, content_type='application/json')
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
		self.assertTrue(data.has_key('profiles'))
		profiles = data['profiles']
		self.assertTrue(isinstance(profiles, list))
		self.assertEqual(len(profiles), c_count)
		for i in profiles:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('age'))
			self.assertTrue(i.has_key('allAboutYou'))
			self.assertTrue(i.has_key('avatar'))
			self.assertTrue(i.has_key('current'))
			self.assertTrue(isinstance(i['current'], dict))
			self.assertTrue(i.has_key('firstName'))
			self.assertTrue(i.has_key('lastName'))
			self.assertTrue(i.has_key('languages'))
			self.assertTrue(isinstance(i['languages'], list))
			self.assertTrue(i.has_key('online'))
			self.assertTrue(i.has_key('replyRate'))
			self.assertTrue(i.has_key('replyTime'))
			self.assertTrue(i.has_key('profileId'))
			self.assertTrue(i.has_key('dateJoined'))
			#Check if the values are correct....
			aux_prof = UserProfile.objects.filter(pk=i['profileId'])
			self.assertEqual(len(aux_prof), 1)

		# More basics. This time we only select male
		c_count = 2
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=all&type=Host&gender=Male&startDate=2013-03-15&page=1', HTTP_X_AUTH_TOKEN=token1, content_type='application/json')
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
		self.assertTrue(data.has_key('profiles'))
		profiles = data['profiles']
		self.assertTrue(isinstance(profiles, list))
		self.assertEqual(len(profiles), c_count)
		for i in profiles:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('age'))
			self.assertTrue(i.has_key('allAboutYou'))
			self.assertTrue(i.has_key('avatar'))
			self.assertTrue(i.has_key('current'))
			self.assertTrue(isinstance(i['current'], dict))
			self.assertTrue(i.has_key('firstName'))
			self.assertTrue(i.has_key('lastName'))
			self.assertTrue(i.has_key('languages'))
			self.assertTrue(isinstance(i['languages'], list))
			self.assertTrue(i.has_key('online'))
			self.assertTrue(i.has_key('replyRate'))
			self.assertTrue(i.has_key('replyTime'))
			self.assertTrue(i.has_key('profileId'))
			self.assertTrue(i.has_key('dateJoined'))
			#Check if the values are correct....
			aux_prof = UserProfile.objects.filter(pk=i['profileId'])
			self.assertEqual(len(aux_prof), 1)

		# More basics. This time we select capacity >=3 and language english
		c_count = 0
		r1 = c.get('/api/v1/profiles?capacity=3&startAge=18&endAge=99&language=english&type=Host&gender=Both&startDate=2013-03-15&page=1', HTTP_X_AUTH_TOKEN=token1, content_type='application/json')
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
		self.assertTrue(data.has_key('profiles'))
		profiles = data['profiles']
		self.assertTrue(isinstance(profiles, list))
		self.assertEqual(len(profiles), c_count)
		for i in profiles:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('age'))
			self.assertTrue(i.has_key('allAboutYou'))
			self.assertTrue(i.has_key('avatar'))
			self.assertTrue(i.has_key('current'))
			self.assertTrue(isinstance(i['current'], dict))
			self.assertTrue(i.has_key('firstName'))
			self.assertTrue(i.has_key('lastName'))
			self.assertTrue(i.has_key('languages'))
			self.assertTrue(isinstance(i['languages'], list))
			self.assertTrue(i.has_key('online'))
			self.assertTrue(i.has_key('replyRate'))
			self.assertTrue(i.has_key('replyTime'))
			self.assertTrue(i.has_key('profileId'))
			self.assertTrue(i.has_key('dateJoined'))
			#Check if the values are correct....
			aux_prof = UserProfile.objects.filter(pk=i['profileId'])
			self.assertEqual(len(aux_prof), 1)

class PublicRequestTest(TestCase):

	def setUp(self):
		self.lang1 = G(Language, name= 'english')
		self.lang2 = G(Language, name= 'spanish')
		self.lang3 = G(Language, name= 'french')
		self.lang4 = G(Language, name= 'catalan')
		self.lang5 = G(Language, name= 'japanese')

		self.city1 = G(City, name='Barcelona')
		self.city2 = G(City, name='Tokyo')
		self.city3 = G(City, name='Tolouse')
		self.city4 = G(City, name='London')
		self.city5 = G(City, name='Fachadolid')

		self.profile1 = G(UserProfile, birthday = '1985-09-12', gender= 'Male') ## 27 ays
		self.lang1_1 = G(UserLanguage, user_profile= self.profile1, language=self.lang1)
		self.wing1 = G(PublicRequestWing, author=self.profile1, capacity=1, date_start=datetime.today() - timedelta(days=5), date_end=datetime.today() - timedelta(days=2), city=self.city1, type='Accomodation', introduction="HOLA")	#NO	

		self.profile2 = G(UserProfile, birthday = '1981-09-12', gender= 'Female') ## 31 anys
		self.lang2_1 = G(UserLanguage, user_profile= self.profile2, language=self.lang2)
		self.wing2 = G(PublicRequestWing, author=self.profile2, capacity=2, date_start=datetime.today() + timedelta(days=1), date_end=datetime.today() + timedelta(days=4), city=self.city1, type='Accomodation', introduction="HOLA") #YES

		self.profile3 = G(UserProfile, birthday = '1989-09-12', gender= 'Male') ## 23 anys
		self.lang3_1 = G(UserLanguage, user_profile= self.profile3, language=self.lang3)
		self.wing3 = G(PublicRequestWing, author=self.profile3, capacity=3, date_start=datetime.today(), date_end=datetime.today() + timedelta(days=2), city=self.city1, type='Accomodation', introduction="HOLA") #YES

		self.profile4 = G(UserProfile, birthday = '1965-09-12', gender= 'Female') ##47 anys
		self.lang4_1 = G(UserLanguage, user_profile= self.profile4, language=self.lang4)
		self.wing4 = G(PublicRequestWing, author=self.profile4, capacity=4, date_start=datetime.today() - timedelta(days=1), date_end=datetime.today() + timedelta(days=2), city=self.city1, type='Accomodation', introduction="HOLA") #YES

		self.profile5 = G(UserProfile, birthday = '1975-09-12', gender= 'Male') ## 37 anys
		self.lang5_1 = G(UserLanguage, user_profile= self.profile5, language=self.lang5)
		self.wing5 = G(PublicRequestWing, author=self.profile5, capacity=5, date_start=datetime.today() + timedelta(days=2), date_end=datetime.today() + timedelta(days=4), city=self.city2, type='Accomodation', introduction="HOLA") #NO

	def test_search_filtering(self):
		c = Client()
		token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token
		c_count= 4
		start_date = datetime.today()
		end_date = datetime.today() + timedelta(days=8)
		# Basci search, we dont check the sorting yet...
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=all&type=Applicant&gender=Both&page=1', HTTP_X_AUTH_TOKEN=token1, content_type='application/json')
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
		self.assertTrue(data.has_key('profiles'))
		profiles = data['profiles']
		self.assertTrue(isinstance(profiles, list))
		self.assertEqual(len(profiles), c_count)
		for i in profiles:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('age'))
			self.assertTrue(i.has_key('allAboutYou'))
			self.assertTrue(i.has_key('avatar'))
			self.assertTrue(i.has_key('current'))
			self.assertTrue(isinstance(i['current'], dict))
			self.assertTrue(i.has_key('firstName'))
			self.assertTrue(i.has_key('lastName'))
			self.assertTrue(i.has_key('languages'))
			self.assertTrue(isinstance(i['languages'], list))
			self.assertTrue(i.has_key('online'))
			self.assertTrue(i.has_key('replyRate'))
			self.assertTrue(i.has_key('replyTime'))
			self.assertTrue(i.has_key('profileId'))
			self.assertTrue(i.has_key('dateJoined'))
			self.assertTrue(i.has_key('wingIntroduction'))
			self.assertTrue(i.has_key('wingType'))
			self.assertTrue(i.has_key('wingCity'))
			self.assertTrue(i.has_key('wingStartDate'))
			self.assertTrue(i.has_key('wingEndDate'))
			self.assertTrue(i.has_key('wingCapacity'))
			#Check if the values are correct....
			aux_prof = UserProfile.objects.filter(pk=i['profileId'])
			self.assertEqual(len(aux_prof), 1)


		c_count= 3
		start_date = datetime.today()
		end_date = datetime.today() + timedelta(days=8)
		# Only Barcelona
		r1 = c.get('/api/v1/profiles?capacity=1&startAge=18&endAge=99&language=all&type=Applicant&gender=Both&page=1&wings=bArcelona', HTTP_X_AUTH_TOKEN=token1, content_type='application/json')
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
		self.assertTrue(data.has_key('profiles'))
		profiles = data['profiles']
		self.assertTrue(isinstance(profiles, list))
		self.assertEqual(len(profiles), c_count)
		for i in profiles:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('age'))
			self.assertTrue(i.has_key('allAboutYou'))
			self.assertTrue(i.has_key('avatar'))
			self.assertTrue(i.has_key('current'))
			self.assertTrue(isinstance(i['current'], dict))
			self.assertTrue(i.has_key('firstName'))
			self.assertTrue(i.has_key('lastName'))
			self.assertTrue(i.has_key('languages'))
			self.assertTrue(isinstance(i['languages'], list))
			self.assertTrue(i.has_key('online'))
			self.assertTrue(i.has_key('replyRate'))
			self.assertTrue(i.has_key('replyTime'))
			self.assertTrue(i.has_key('profileId'))
			self.assertTrue(i.has_key('dateJoined'))
			self.assertTrue(i.has_key('wingIntroduction'))
			self.assertTrue(i.has_key('wingType'))
			self.assertTrue(i.has_key('wingCity'))
			self.assertTrue(i.has_key('wingStartDate'))
			self.assertTrue(i.has_key('wingEndDate'))
			self.assertTrue(i.has_key('wingCapacity'))
			#Check if the values are correct....
			aux_prof = UserProfile.objects.filter(pk=i['profileId'])
			self.assertEqual(len(aux_prof), 1)

class ControlTest(TestCase):

	def setUp(self):		

		self.profile1 = G(UserProfile, birthday = '1985-09-12', gender= 'Male') ## 27 ays
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token

	def test_search_filtering(self):
		c = Client()
		
		c_count= 4
		start_date = datetime.today()
		end_date = datetime.today() + timedelta(days=8)
		# Basci search, we dont check the sorting yet...
		r1 = c.get('/api/v1/control', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)	


class ProfileTest(TestCase):

	def setUp(self):		

		self.user1 = G(User, first_name='Joan', last_name= 'Roca', email='fr33d4n@peoplewings.com', is_active=True)
		self.city1 = G(City, name='Barcelona', lat=41.1, lon=1.2, region=G(Region, name='Catalonia', country=G(Country, name='Spain')))
		self.profile1 = G(UserProfile, pk= self.user1.pk, user= self.user1, pw_state = 'Y', birthday = '1985-09-12', show_birthday= 'F', gender= 'Male', civil_state='SI', current_city = self.city1, hometown=self.city1, email='fuck@you.com', phone='606762696') ## 27 ays
		self.token1 = ApiToken.objects.create(user=self.user1, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2037 00:00', '%d-%m-%Y %H:%M')).token

	def test_profiles_id(self):
		c = Client()
		#Let's check if we can see our own profile
		r1 = c.get('/api/v1/profiles/%s' % self.profile1.pk, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)	

		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		data = content['data']

		self.assertTrue(data.has_key("interestedIn"))
		self.assertTrue(isinstance(data['interestedIn'], list))
		for i in data['interestedIn']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('gender'))

		self.assertTrue(data.has_key("hometown"))
		self.assertTrue(isinstance(data['hometown'], dict))
		self.assertTrue(data['hometown'].has_key('lat'))
		self.assertEqual(data['hometown']['lat'], str(self.city1.lat))
		self.assertTrue(data['hometown'].has_key('lon'))
		self.assertEqual(data['hometown']['lon'], str(self.city1.lon))
		self.assertTrue(data['hometown'].has_key('region'))
		self.assertEqual(data['hometown']['region'], self.city1.region.name)
		self.assertTrue(data['hometown'].has_key('country'))
		self.assertEqual(data['hometown']['country'], self.city1.region.country.name)

		self.assertTrue(data.has_key("replyTime"))
		self.assertEqual(data["replyTime"], self.profile1.reply_time)

		self.assertTrue(data.has_key("mainMission"))
		self.assertEqual(data["mainMission"], self.profile1.main_mission)
		
		self.assertTrue(data.has_key("birthMonth"))
		self.assertEqual(data["birthMonth"], str(self.profile1.birthday.month))

		self.assertTrue(data.has_key("civilState"))
		self.assertEqual(data["civilState"], self.profile1.civil_state)

		self.assertTrue(data.has_key("personalPhilosophy"))
		self.assertEqual(data["personalPhilosophy"], self.profile1.personal_philosphy)

		self.assertTrue(data.has_key("lastLoginDate"))
		self.assertEqual(data["lastLoginDate"], 'ON')

		self.assertTrue(data.has_key("education"))
		self.assertTrue(isinstance(data['education'], list))
		for i in data['education']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('institution'))
			self.assertTrue(i.has_key('degree'))

		self.assertTrue(data.has_key("id"))
		self.assertEqual(data['id'], self.profile1.pk)

		self.assertTrue(data.has_key("occupation"))
		self.assertEqual(data['occupation'], self.profile1.occupation)

		self.assertTrue(data.has_key("current"))
		self.assertTrue(isinstance(data['current'], dict))
		self.assertTrue(data['current'].has_key('lat'))
		self.assertEqual(data['current']['lat'], str(self.city1.lat))
		self.assertTrue(data['current'].has_key('lon'))
		self.assertEqual(data['current']['lon'], str(self.city1.lon))
		self.assertTrue(data['current'].has_key('region'))
		self.assertEqual(data['current']['region'], self.city1.region.name)
		self.assertTrue(data['current'].has_key('country'))
		self.assertEqual(data['current']['country'], self.city1.region.country.name)

		self.assertTrue(data.has_key("pwState"))
		self.assertEqual(data['pwState'], self.profile1.pw_state)

		self.assertTrue(data.has_key("incredible"))
		self.assertEqual(data['incredible'], self.profile1.incredible)

		self.assertTrue(data.has_key("otherLocations"))
		self.assertTrue(isinstance(data['otherLocations'], list))
		for i in data['otherLocations']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('lat'))
		self.assertTrue(i.has_key('lon'))
		self.assertTrue(i.has_key('region'))
		self.assertTrue(i.has_key('country'))

		self.assertTrue(data.has_key("sports"))
		self.assertEqual(data['sports'], self.profile1.sports)

		self.assertTrue(data.has_key("languages"))
		self.assertTrue(isinstance(data['languages'], list))
		for i in data['languages']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('name'))
		self.assertTrue(i.has_key('level'))

		self.assertTrue(data.has_key("birthYear"))
		self.assertEqual(data['birthYear'], str(self.profile1.birthday.year))

		self.assertTrue(data.has_key("quotes"))
		self.assertEqual(data['quotes'], self.profile1.quotes)

		self.assertTrue(data.has_key("socialNetworks"))
		self.assertTrue(isinstance(data['socialNetworks'], list))
		for i in data['socialNetworks']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('snUsername'))
		self.assertTrue(i.has_key('socialNetwork'))

		self.assertTrue(data.has_key("online"))
		self.assertEqual(data['online'], 'ON')

		self.assertTrue(data.has_key("sharing"))
		self.assertEqual(data['sharing'], self.profile1.sharing)	  
		  
		self.assertTrue(data.has_key("pwOpinion"))
		self.assertEqual(data['pwOpinion'], self.profile1.pw_opinion)	  

		self.assertTrue(data.has_key("politicalOpinion"))
		self.assertEqual(data['politicalOpinion'], self.profile1.political_opinion)	  

		self.assertTrue(data.has_key("company"))
		self.assertEqual(data['company'], self.profile1.company)	  

		self.assertTrue(data.has_key("replyRate"))
		self.assertEqual(data['replyRate'], self.profile1.reply_rate)	  

		self.assertTrue(data.has_key("instantMessages"))
		self.assertTrue(isinstance(data['instantMessages'], list))
		for i in data['instantMessages']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('imUsername'))
		self.assertTrue(i.has_key('instantMessage'))

		self.assertTrue(data.has_key("phone"))
		self.assertEqual(data['phone'], self.profile1.phone)

		self.assertTrue(data.has_key("active"))
		self.assertEqual(data['active'], self.profile1.active)

		self.assertTrue(data.has_key("emails"))
		self.assertEqual(data['emails'], self.profile1.emails)

		self.assertTrue(data.has_key("inspiredBy"))
		self.assertEqual(data['inspiredBy'], self.profile1.inspired_by)

		self.assertTrue(data.has_key("otherPages"))
		self.assertEqual(data['otherPages'], self.profile1.other_pages)

		self.assertTrue(data.has_key("firstName"))
		self.assertEqual(data['firstName'], self.profile1.first_name)

		self.assertTrue(data.has_key("enjoyPeople"))
		self.assertEqual(data['enjoyPeople'], self.profile1.enjoy_people)

		self.assertTrue(data.has_key("gender"))
		self.assertEqual(data['gender'], self.profile1.gender)

		self.assertTrue(data.has_key("age"))
		self.assertEqual(data['age'], "27")

		self.assertTrue(data.has_key("allAboutYou"))
		self.assertEqual(data['allAboutYou'], self.profile1.all_about_you)

		self.assertTrue(data.has_key("movies"))
		self.assertEqual(data['movies'], self.profile1.movies)

		self.assertTrue(data.has_key("birthDay"))
		self.assertEqual(data['birthDay'], str(self.profile1.birthday.day))

		self.assertTrue(data.has_key("avatar"))
		self.assertEqual(data['avatar'], self.profile1.avatar)

		self.assertTrue(data.has_key("lastLogin"))
		self.assertTrue(isinstance(data['lastLogin'], dict))
		self.assertTrue(data['lastLogin'].has_key('lat'))
		self.assertEqual(data['lastLogin']['lat'], str(self.city1.lat))
		self.assertTrue(data['lastLogin'].has_key('lon'))
		self.assertEqual(data['lastLogin']['lon'], str(self.city1.lon))
		self.assertTrue(data['lastLogin'].has_key('region'))
		self.assertEqual(data['lastLogin']['region'], self.city1.region.name)
		self.assertTrue(data['lastLogin'].has_key('country'))
		self.assertEqual(data['lastLogin']['country'], self.city1.region.country.name)

		self.assertTrue(data.has_key("lastName"))
		self.assertEqual(data['lastName'], self.profile1.last_name)

		self.assertTrue(data.has_key("religion"))
		self.assertEqual(data['religion'], self.profile1.religion)

		self.assertTrue(data.has_key("showBirthday"))
		self.assertEqual(data['showBirthday'], self.profile1.show_birthday)	

		#Lets see what happens if another user besides me tryes to see my profile (without preview) (AUTH REQUIRED)
		r1 = c.get('/api/v1/profiles/%s' % self.profile1.pk, HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], False)	

	def test_profiles_id_preview(self):
		c = Client()
		#Let's check if we can see our own profile as preview
		r1 = c.get('/api/v1/profiles/%s/preview' % self.profile1.pk, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)	

		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		data = content['data']

		self.assertTrue(data.has_key("interestedIn"))
		self.assertTrue(isinstance(data['interestedIn'], list))
		for i in data['interestedIn']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('gender'))

		self.assertTrue(data.has_key("hometown"))
		self.assertTrue(isinstance(data['hometown'], dict))
		self.assertTrue(data['hometown'].has_key('lat'))
		self.assertEqual(data['hometown']['lat'], str(self.city1.lat))
		self.assertTrue(data['hometown'].has_key('lon'))
		self.assertEqual(data['hometown']['lon'], str(self.city1.lon))
		self.assertTrue(data['hometown'].has_key('region'))
		self.assertEqual(data['hometown']['region'], self.city1.region.name)
		self.assertTrue(data['hometown'].has_key('country'))
		self.assertEqual(data['hometown']['country'], self.city1.region.country.name)

		self.assertTrue(data.has_key("replyTime"))
		self.assertEqual(data["replyTime"], self.profile1.reply_time)

		self.assertTrue(data.has_key("mainMission"))
		self.assertEqual(data["mainMission"], self.profile1.main_mission)

		self.assertTrue(data.has_key("civilState"))
		self.assertEqual(data["civilState"], self.profile1.civil_state)

		self.assertTrue(data.has_key("personalPhilosophy"))
		self.assertEqual(data["personalPhilosophy"], self.profile1.personal_philosphy)

		self.assertTrue(data.has_key("lastLoginDate"))
		self.assertEqual(data["lastLoginDate"], 'ON')

		self.assertTrue(data.has_key("education"))
		self.assertTrue(isinstance(data['education'], list))
		for i in data['education']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('institution'))
			self.assertTrue(i.has_key('degree'))

		self.assertTrue(data.has_key("id"))
		self.assertEqual(data['id'], self.profile1.pk)

		self.assertTrue(data.has_key("occupation"))
		self.assertEqual(data['occupation'], self.profile1.occupation)

		self.assertTrue(data.has_key("current"))
		self.assertTrue(isinstance(data['current'], dict))
		self.assertTrue(data['current'].has_key('lat'))
		self.assertEqual(data['current']['lat'], str(self.city1.lat))
		self.assertTrue(data['current'].has_key('lon'))
		self.assertEqual(data['current']['lon'], str(self.city1.lon))
		self.assertTrue(data['current'].has_key('region'))
		self.assertEqual(data['current']['region'], self.city1.region.name)
		self.assertTrue(data['current'].has_key('country'))
		self.assertEqual(data['current']['country'], self.city1.region.country.name)

		self.assertTrue(data.has_key("pwState"))
		self.assertEqual(data['pwState'], self.profile1.pw_state)

		self.assertTrue(data.has_key("incredible"))
		self.assertEqual(data['incredible'], self.profile1.incredible)

		self.assertTrue(data.has_key("otherLocations"))
		self.assertTrue(isinstance(data['otherLocations'], list))
		for i in data['otherLocations']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('lat'))
		self.assertTrue(i.has_key('lon'))
		self.assertTrue(i.has_key('region'))
		self.assertTrue(i.has_key('country'))

		self.assertTrue(data.has_key("sports"))
		self.assertEqual(data['sports'], self.profile1.sports)

		self.assertTrue(data.has_key("languages"))
		self.assertTrue(isinstance(data['languages'], list))
		for i in data['languages']:
			self.assertTrue(isinstance(i, dict))
			self.assertTrue(i.has_key('name'))
		self.assertTrue(i.has_key('level'))

		self.assertTrue(data.has_key("birthday"))
		self.assertEqual(data['birthday'],  '1985-09-12')

		self.assertTrue(data.has_key("quotes"))
		self.assertEqual(data['quotes'], self.profile1.quotes)

		self.assertFalse(data.has_key("socialNetworks"))

		self.assertTrue(data.has_key("online"))
		self.assertEqual(data['online'], 'ON')

		self.assertTrue(data.has_key("sharing"))
		self.assertEqual(data['sharing'], self.profile1.sharing)	  
		  
		self.assertTrue(data.has_key("pwOpinion"))
		self.assertEqual(data['pwOpinion'], self.profile1.pw_opinion)	  

		self.assertTrue(data.has_key("politicalOpinion"))
		self.assertEqual(data['politicalOpinion'], self.profile1.political_opinion)	  

		self.assertTrue(data.has_key("company"))
		self.assertEqual(data['company'], self.profile1.company)	  

		self.assertTrue(data.has_key("replyRate"))
		self.assertEqual(data['replyRate'], self.profile1.reply_rate)	  

		self.assertFalse(data.has_key("instantMessages"))

		self.assertFalse(data.has_key("phone"))

		self.assertTrue(data.has_key("active"))
		self.assertEqual(data['active'], self.profile1.active)

		self.assertFalse(data.has_key("emails"))

		self.assertTrue(data.has_key("inspiredBy"))
		self.assertEqual(data['inspiredBy'], self.profile1.inspired_by)

		self.assertTrue(data.has_key("otherPages"))
		self.assertEqual(data['otherPages'], self.profile1.other_pages)

		self.assertTrue(data.has_key("firstName"))
		self.assertEqual(data['firstName'], self.profile1.first_name)

		self.assertTrue(data.has_key("enjoyPeople"))
		self.assertEqual(data['enjoyPeople'], self.profile1.enjoy_people)

		self.assertTrue(data.has_key("gender"))
		self.assertEqual(data['gender'], self.profile1.gender)

		self.assertTrue(data.has_key("age"))
		self.assertEqual(data['age'], "27")

		self.assertTrue(data.has_key("allAboutYou"))
		self.assertEqual(data['allAboutYou'], self.profile1.all_about_you)

		self.assertTrue(data.has_key("movies"))
		self.assertEqual(data['movies'], self.profile1.movies)

		self.assertTrue(data.has_key("avatar"))
		self.assertEqual(data['avatar'], self.profile1.avatar)

		self.assertTrue(data.has_key("lastLogin"))
		self.assertTrue(isinstance(data['lastLogin'], dict))
		self.assertTrue(data['lastLogin'].has_key('lat'))
		self.assertEqual(data['lastLogin']['lat'], str(self.city1.lat))
		self.assertTrue(data['lastLogin'].has_key('lon'))
		self.assertEqual(data['lastLogin']['lon'], str(self.city1.lon))
		self.assertTrue(data['lastLogin'].has_key('region'))
		self.assertEqual(data['lastLogin']['region'], self.city1.region.name)
		self.assertTrue(data['lastLogin'].has_key('country'))
		self.assertEqual(data['lastLogin']['country'], self.city1.region.country.name)

		self.assertTrue(data.has_key("lastName"))
		self.assertEqual(data['lastName'], self.profile1.last_name)

		self.assertTrue(data.has_key("religion"))
		self.assertEqual(data['religion'], self.profile1.religion)

		self.assertFalse(data.has_key("showBirthday"))

		#Let's change the show birthday attr. Let's put it in Partial (P)
		self.profile1.show.birthday = 'P'
		self.profile1.save()

		r1 = c.get('/api/v1/profiles/%s/preview' % self.profile1.pk, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)	

		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		data = content['data']

		self.assertTrue(data.has_key("birthday"))
		self.assertEqual(data['birthday'],  '09-12')

		#Let's change the show birthday attr. Let's put it in None (N)
		self.profile1.show.birthday = 'N'
		self.profile1.save()

		r1 = c.get('/api/v1/profiles/%s/preview' % self.profile1.pk, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r1.status_code, 200)
		content = json.loads(r1.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)	

		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		data = content['data']

		self.assertTrue(data.has_key("birthday"))
		self.assertEqual(data['birthday'],  '')

		

