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
from django_dynamic_fixture import G, F
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.wings.models import Accomodation, PublicTransport
from peoplewings.apps.locations.models import City
from django.contrib.auth.models import User
from people.models import UserProfile
from peoplewings.libs.customauth.models import ApiToken

from django.utils.timezone import utc
from pprint import pprint

 
class ListWingsNamesTest(TestCase):

	def setUp(self):
		# creamos profiles varios...
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		self.profile3 = G(UserProfile)
		self.token3 = ApiToken.objects.create(user=self.profile3.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

		# creamos 2 accomodations del usuario 1 y 1 accomodation del usuario 3
		self.a1 = G(Accomodation, author=self.profile1)
		self.a2 = G(Accomodation, author=self.profile1)
		self.a3 = G(Accomodation, author=self.profile3)

	def test_list_wings(self):
		c = Client()
		
		# user 1 wants to see wings of user 2 => empty list
		r = c.get('/api/v1/wings?profile='+str(self.profile2.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 0)

		# user 1 wants to see wings of user 3 => 1 wing
		r = c.get('/api/v1/wings?profile='+str(self.profile3.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 1)
		l1_item= l1[0]
		self.assertTrue(l1_item.has_key('wingName'))
		self.assertEqual(l1_item['wingName'], self.a3.name)
		self.assertTrue(l1_item.has_key('idWing'))
		self.assertEqual(l1_item['idWing'], self.a3.id)
		self.assertTrue(l1_item.has_key('wingType'))
		self.assertEqual(l1_item['wingType'], "Accomodation")


		# check that user 2 sees the same list as user 1 when looking for wings of user 3
		r = c.get('/api/v1/wings?profile='+str(self.profile3.pk), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l2 = content['data']['items']
		self.assertEqual(l1, l2)

		# user 2 wants to see wings of user 1 => 2 wings
		r = c.get('/api/v1/wings?profile='+str(self.profile1.pk), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(r.status_code, 200)
		content = json.loads(r.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], dict))
		self.assertTrue(content['data'].has_key('items'))
		l1 = content['data']['items']
		self.assertEqual(len(l1), 2)
		l1_item = l1[0]
		self.assertTrue(l1_item.has_key('wingName'))
		self.assertEqual(l1_item['wingName'], self.a1.name)
		self.assertTrue(l1_item.has_key('idWing'))
		self.assertEqual(l1_item['idWing'], self.a1.pk)
		self.assertTrue(l1_item.has_key('wingType'))
		self.assertEqual(l1_item['wingType'], "Accomodation")
		l1_item = l1[1]
		self.assertTrue(l1_item.has_key('wingName'))
		self.assertEqual(l1_item['wingName'], self.a2.name)
		self.assertTrue(l1_item.has_key('idWing'))
		self.assertEqual(l1_item['idWing'], self.a2.pk)
		self.assertTrue(l1_item.has_key('wingType'))
		self.assertEqual(l1_item['wingType'], "Accomodation")

		
class AccomodationTest(TestCase):

	def setUp(self):
		# creamos profiles varios...
		self.profile1 = G(UserProfile)
		self.token1 = ApiToken.objects.create(user=self.profile1.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token
		self.city1= G(City, name='Barcelona', region=F(name='Catalonia', country = F(name='Spain')))
		self.trans1= G(PublicTransport, name='bus')
		self.trans2= G(PublicTransport, name='tram')
		self.trans3= G(PublicTransport, name='train')
		self.trans4= G(PublicTransport, name='boat')
		self.trans5= G(PublicTransport, name='underground')
		self.trans6= G(PublicTransport, name='others')

		self.wd1_name= 'Sinsui'
		self.wd1_status='Y'
		self.wd1_best_days='W'
		self.wd1_is_request= False
		self.wd1_city= self.city1
		self.wd1_active= True
		self.wd1_sharing_once= False
		self.wd1_capacity= 2
		self.wd1_preferred_male= False
		self.wd1_preferred_female= True
		self.wd1_wheelchair= False
		self.wd1_where_sleeping_type= 'C'
		self.wd1_smoking= 'S'
		self.wd1_i_have_pet= False
		self.wd1_pets_allowed= False
		self.wd1_blankets= False
		self.wd1_live_center= False
		self.wd1_public_transport= [self.trans1, self.trans2]
		self.wd1_about= 'asdads'
		self.wd1_address='asdadsdddd'
		self.wd1_number='123'
		self.wd1_additional_information= 'Fino filipino'
		self.wd1_postal_code= '09023'
		self.a1 = G(Accomodation, author=self.profile1, name= self.wd1_name, status= self.wd1_status, best_days= self.wd1_best_days, is_request= self.wd1_is_request, city= self.wd1_city, active= self.wd1_active, sharing_once= self.wd1_sharing_once,
			capacity= self.wd1_capacity, preferred_male= self.wd1_preferred_male, preferred_female= self.wd1_preferred_female, wheelchair= self.wd1_wheelchair, where_sleeping_type= self.wd1_where_sleeping_type, smoking= self.wd1_smoking,
			i_have_pet= self.wd1_i_have_pet, pets_allowed= self.wd1_pets_allowed, blankets= self.wd1_blankets, live_center= self.wd1_live_center, public_transport= self.wd1_public_transport, about= self.wd1_about, address= self.wd1_address,
			number= self.wd1_number, additional_information= self.wd1_additional_information, postal_code= self.wd1_postal_code)

		self.profile2 = G(UserProfile)
		self.token2 = ApiToken.objects.create(user=self.profile2.user, last = datetime.strptime('01-01-2200 00:00', '%d-%m-%Y %H:%M')).token

	def test_get_wings(self):
		c = Client()
		response = c.get('/api/v1/profiles/%s/accomodations' % (self.profile1.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')

		#Correct call without preview
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], list))
		for i in content['data']:
			data=i
			self.assertTrue(data.has_key('address'))
			self.assertEqual(data['address'], self.wd1_address)
			self.assertTrue(data.has_key('number'))
			self.assertEqual(data['number'], self.wd1_number)
			self.assertTrue(data.has_key('liveCenter'))
			self.assertEqual(data['liveCenter'], self.wd1_live_center)
			self.assertTrue(data.has_key('id'))
			self.assertTrue(data.has_key('boat'))
			self.assertEqual(data['boat'], False)
			self.assertTrue(data.has_key('city'))
			self.assertTrue(isinstance(data['city'], dict))
			city = data['city']
			self.assertTrue(city.has_key('lat'))
			self.assertTrue(city.has_key('lon'))
			self.assertTrue(city.has_key('region'))
			self.assertTrue(city.has_key('country'))
			self.assertTrue(city.has_key('name'))
			self.assertTrue(data.has_key('capacity'))
			self.assertEqual(data['capacity'], str(self.wd1_capacity))
			self.assertTrue(data.has_key('whereSleepingType'))
			self.assertEqual(data['whereSleepingType'], self.wd1_where_sleeping_type)
			self.assertTrue(data.has_key('dateEnd'))
			self.assertTrue(data.has_key('bestDays'))
			self.assertEqual(data['bestDays'], self.wd1_best_days)
			self.assertTrue(data.has_key('postalCode'))
			self.assertEqual(data['postalCode'], self.wd1_postal_code)
			self.assertTrue(data.has_key('status'))
			self.assertEqual(data['status'], self.wd1_status)
			self.assertTrue(data.has_key('wheelchair'))
			self.assertEqual(data['wheelchair'], self.wd1_wheelchair)
			self.assertFalse(data.has_key('resourceUri'))
			self.assertTrue(data.has_key('dateStart'))
			self.assertTrue(data.has_key('bus'))
			self.assertEqual(data['bus'], True)
			self.assertTrue(data.has_key('metro'))
			self.assertEqual(data['metro'], False)
			self.assertTrue(data.has_key('train'))
			self.assertEqual(data['train'], False)
			self.assertTrue(data.has_key('petsAllowed'))
			self.assertEqual(data['petsAllowed'], self.wd1_pets_allowed)
			self.assertTrue(data.has_key('others'))
			self.assertEqual(data['others'], False)
			self.assertFalse(data.has_key('active'))
			self.assertTrue(data.has_key('smoking'))
			self.assertEqual(data['smoking'], self.wd1_smoking)
			self.assertTrue(data.has_key('iHavePet'))
			self.assertEqual(data['iHavePet'], self.wd1_i_have_pet)
			self.assertTrue(data.has_key('blankets'))
			self.assertEqual(data['blankets'], self.wd1_blankets)
			self.assertTrue(data.has_key('about'))
			self.assertEqual(data['about'], self.wd1_about)
			self.assertTrue(data.has_key('name'))
			self.assertEqual(data['name'], self.wd1_name)
			self.assertTrue(data.has_key('tram'))
			self.assertEqual(data['tram'], True)
			self.assertFalse(data.has_key('isRequest'))
			self.assertTrue(data.has_key('sharingOnce'))
			self.assertEqual(data['sharingOnce'], self.wd1_sharing_once)
			self.assertTrue(data.has_key('preferredMale'))
			self.assertEqual(data['preferredMale'], self.wd1_preferred_male)
			self.assertTrue(data.has_key('preferredFemale'))
			self.assertEqual(data['preferredFemale'], self.wd1_preferred_female)
			self.assertTrue(data.has_key('additionalInformation'))
			self.assertEqual(data['additionalInformation'], self.wd1_additional_information)

		#Correct call with preview

		response = c.get('/api/v1/profiles/%s/accomodations/preview' % (self.profile1.pk), HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)
		
		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], list))
		for i in content['data']:
			data=i
			self.assertFalse(data.has_key('address'))
			self.assertFalse(data.has_key('number'))
			self.assertTrue(data.has_key('liveCenter'))
			self.assertEqual(data['liveCenter'], self.wd1_live_center)
			self.assertTrue(data.has_key('id'))
			self.assertTrue(data.has_key('boat'))
			self.assertEqual(data['boat'], False)
			self.assertTrue(data.has_key('city'))
			city = data['city']
			self.assertTrue(city.has_key('lat'))
			self.assertTrue(city.has_key('lon'))
			self.assertTrue(city.has_key('region'))
			self.assertTrue(city.has_key('country'))
			self.assertTrue(city.has_key('name'))
			self.assertTrue(data.has_key('capacity'))
			self.assertEqual(data['capacity'], str(self.wd1_capacity))
			self.assertTrue(data.has_key('whereSleepingType'))
			self.assertEqual(data['whereSleepingType'], self.wd1_where_sleeping_type)
			self.assertTrue(data.has_key('dateEnd'))
			self.assertTrue(data.has_key('bestDays'))
			self.assertEqual(data['bestDays'], self.wd1_best_days)
			self.assertFalse(data.has_key('postalCode'))
			self.assertTrue(data.has_key('status'))
			self.assertEqual(data['status'], self.wd1_status)
			self.assertTrue(data.has_key('wheelchair'))
			self.assertEqual(data['wheelchair'], self.wd1_wheelchair)
			self.assertFalse(data.has_key('resourceUri'))
			self.assertTrue(data.has_key('dateStart'))
			self.assertTrue(data.has_key('bus'))
			self.assertEqual(data['bus'], True)
			self.assertTrue(data.has_key('metro'))
			self.assertEqual(data['metro'], False)
			self.assertTrue(data.has_key('train'))
			self.assertEqual(data['train'], False)
			self.assertTrue(data.has_key('petsAllowed'))
			self.assertEqual(data['petsAllowed'], self.wd1_pets_allowed)
			self.assertTrue(data.has_key('others'))
			self.assertEqual(data['others'], False)
			self.assertFalse(data.has_key('active'))
			self.assertTrue(data.has_key('smoking'))
			self.assertEqual(data['smoking'], self.wd1_smoking)
			self.assertTrue(data.has_key('iHavePet'))
			self.assertEqual(data['iHavePet'], self.wd1_i_have_pet)
			self.assertTrue(data.has_key('blankets'))
			self.assertEqual(data['blankets'], self.wd1_blankets)
			self.assertTrue(data.has_key('about'))
			self.assertEqual(data['about'], self.wd1_about)
			self.assertTrue(data.has_key('name'))
			self.assertEqual(data['name'], self.wd1_name)
			self.assertTrue(data.has_key('tram'))
			self.assertEqual(data['tram'], True)
			self.assertFalse(data.has_key('isRequest'))
			self.assertTrue(data.has_key('sharingOnce'))
			self.assertEqual(data['sharingOnce'], self.wd1_sharing_once)
			self.assertTrue(data.has_key('preferredMale'))
			self.assertEqual(data['preferredMale'], self.wd1_preferred_male)
			self.assertTrue(data.has_key('preferredFemale'))
			self.assertEqual(data['preferredFemale'], self.wd1_preferred_female)
			self.assertFalse(data.has_key('additionalInformation'))

		#Wrong call with no preview but with another profile

		response = c.get('/api/v1/profiles/%s/accomodations/' % (self.profile1.pk), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], False)

		#Correct call with preview and another profile

		response = c.get('/api/v1/profiles/%s/accomodations/preview' % (self.profile1.pk), HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)

		self.assertTrue(content.has_key('data'))
		self.assertTrue(isinstance(content['data'], list))
		for i in content['data']:
			data=i
			self.assertFalse(data.has_key('address'))
			self.assertFalse(data.has_key('number'))
			self.assertTrue(data.has_key('liveCenter'))
			self.assertEqual(data['liveCenter'], self.wd1_live_center)
			self.assertTrue(data.has_key('id'))
			self.assertTrue(data.has_key('boat'))
			self.assertEqual(data['boat'], False)
			self.assertTrue(data.has_key('city'))
			city = data['city']
			self.assertTrue(city.has_key('lat'))
			self.assertTrue(city.has_key('lon'))
			self.assertTrue(city.has_key('region'))
			self.assertTrue(city.has_key('country'))
			self.assertTrue(city.has_key('name'))
			self.assertTrue(data.has_key('capacity'))
			self.assertEqual(data['capacity'], str(self.wd1_capacity))
			self.assertTrue(data.has_key('whereSleepingType'))
			self.assertEqual(data['whereSleepingType'], self.wd1_where_sleeping_type)
			self.assertTrue(data.has_key('dateEnd'))
			self.assertTrue(data.has_key('bestDays'))
			self.assertEqual(data['bestDays'], self.wd1_best_days)
			self.assertFalse(data.has_key('postalCode'))
			self.assertTrue(data.has_key('status'))
			self.assertEqual(data['status'], self.wd1_status)
			self.assertTrue(data.has_key('wheelchair'))
			self.assertEqual(data['wheelchair'], self.wd1_wheelchair)
			self.assertFalse(data.has_key('resourceUri'))
			self.assertTrue(data.has_key('dateStart'))
			self.assertTrue(data.has_key('bus'))
			self.assertEqual(data['bus'], True)
			self.assertTrue(data.has_key('metro'))
			self.assertEqual(data['metro'], False)
			self.assertTrue(data.has_key('train'))
			self.assertEqual(data['train'], False)
			self.assertTrue(data.has_key('petsAllowed'))
			self.assertEqual(data['petsAllowed'], self.wd1_pets_allowed)
			self.assertTrue(data.has_key('others'))
			self.assertEqual(data['others'], False)
			self.assertFalse(data.has_key('active'))
			self.assertTrue(data.has_key('smoking'))
			self.assertEqual(data['smoking'], self.wd1_smoking)
			self.assertTrue(data.has_key('iHavePet'))
			self.assertEqual(data['iHavePet'], self.wd1_i_have_pet)
			self.assertTrue(data.has_key('blankets'))
			self.assertEqual(data['blankets'], self.wd1_blankets)
			self.assertTrue(data.has_key('about'))
			self.assertEqual(data['about'], self.wd1_about)
			self.assertTrue(data.has_key('name'))
			self.assertEqual(data['name'], self.wd1_name)
			self.assertTrue(data.has_key('tram'))
			self.assertEqual(data['tram'], True)
			self.assertFalse(data.has_key('isRequest'))
			self.assertTrue(data.has_key('sharingOnce'))
			self.assertEqual(data['sharingOnce'], self.wd1_sharing_once)
			self.assertTrue(data.has_key('preferredMale'))
			self.assertEqual(data['preferredMale'], self.wd1_preferred_male)
			self.assertTrue(data.has_key('preferredFemale'))
			self.assertEqual(data['preferredFemale'], self.wd1_preferred_female)
			self.assertFalse(data.has_key('additionalInformation'))

	def test_post_wings(self):
		c = Client()
		post_data = json.dumps(		{
			"tram": False,
			"bus": True,
			"metro": False,
			"train": True,
			"others": False,
			"liveCenter": False,
			"petsAllowed": False,
			"wheelchair": True,
			"sharingOnce": False,
			"iHavePet": True,
			"blankets": False,
			"name": "Wing name",
			"status": "Y",
			"bestDays": "A",
			"capacity": "1",
			"preferredGender": "Male",
			"whereSleepingType": "C",
			"smoking": "N",
			"metro": True,
			"about": "Its a nice place to stay",
			"address": "Manila",
			"number": "23",
			"additionalInformation": "Lololol",
			"postalCode": "08025",
			"city": {"lat":41.1, "lon":1.2, "name":"Barcelona", "region":"Catalonia", "country":"Spain"}
			})
		response = c.post('/api/v1/profiles/%s/accomodations' % (self.profile1.pk), post_data, HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content)
		self.assertTrue(content.has_key('status'))
		self.assertEqual(content['status'], True)

		new_list = Accomodation.objects.filter(author=self.profile1).order_by('pk')
		self.assertTrue(len(new_list) == 2)
		new = new_list[1]
		self.assertEqual(new.name, 'Wing name')
		self.assertEqual(new.status, 'Y')
		self.assertEqual(new.date_start, None)
		self.assertEqual(new.date_end, None)
		self.assertEqual(new.best_days, 'A')
		self.assertEqual(new.is_request, False)

		self.assertEqual(new.city, City.objects.get(name='Barcelona'))
		self.assertEqual(new.active, True)
		self.assertEqual(new.sharing_once, False)
		self.assertEqual(new.capacity, '1')
		self.assertEqual(new.preferred_male, True)

		self.assertEqual(new.preferred_female, False)
		self.assertEqual(new.wheelchair, True)
		self.assertEqual(new.where_sleeping_type,'C')
		self.assertEqual(new.smoking, 'N')
		self.assertEqual(new.i_have_pet, True)

		self.assertEqual(new.pets_allowed, False)
		self.assertEqual(new.blankets, False)
		self.assertEqual(new.live_center, False)
		for i in new.public_transport.all():
			self.assertTrue(i in PublicTransport.objects.filter(name__in=['bus', 'train', 'metro']))
		for i in PublicTransport.objects.filter(name__in=['bus', 'train', 'metro']):
			self.assertTrue(i in new.public_transport.all())
			
		self.assertEqual(new.about, "Its a nice place to stay")

		self.assertEqual(new.address, 'Manila')
		self.assertEqual(new.number, '23')
		self.assertEqual(new.additional_information, 'Lololol')
		self.assertEqual(new.postal_code, '08025')
