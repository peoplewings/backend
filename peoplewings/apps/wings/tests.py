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
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.wings.models import Accomodation
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
        self.assertTrue(content.has_key('code'))
        self.assertEqual(content['code'], 200)
        self.assertTrue(content.has_key('msg'))
        self.assertEqual(content['msg'], "Wings retrieved successfully.")
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
        self.assertTrue(content.has_key('code'))
        self.assertEqual(content['code'], 200)
        self.assertTrue(content.has_key('msg'))
        self.assertEqual(content['msg'], "Wings retrieved successfully.")
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
        self.assertTrue(content.has_key('code'))
        self.assertEqual(content['code'], 200)
        self.assertTrue(content.has_key('msg'))
        self.assertEqual(content['msg'], "Wings retrieved successfully.")
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
        self.assertTrue(content.has_key('code'))
        self.assertEqual(content['code'], 200)
        self.assertTrue(content.has_key('msg'))
        self.assertEqual(content['msg'], "Wings retrieved successfully.")
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
