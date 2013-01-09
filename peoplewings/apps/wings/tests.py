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

    def test_not_logged_in(self):
        c = Client()  
        r = c.get('/api/v1/profiles/'+str(self.profile2.pk)+'/wings', content_type='application/json')
        self.assertEqual(json.loads(r.content)['code'], 413)
        self.assertEqual(json.loads(r.content)['msg'], "Unauthorized")
        self.assertEqual(json.loads(r.content)['status'], False)
 
    def test_logged_in(self):
        c = Client()    
        response = c.get('/api/v1/profiles/'+str(self.profile2.pk)+'/wings', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_list_wings(self):
        c = Client()
        
        # user 1 wants to see wings of user 2 => empty list
        r = c.get('/api/v1/profiles/'+str(self.profile2.pk)+'/wings', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
        self.assertEqual(json.loads(r.content)['code'], 200)
        self.assertEqual(json.loads(r.content)['msg'], "Wings retrieved successfully.")
        self.assertEqual(json.loads(r.content)['status'], True)
        l1 = json.loads(r.content)['data']
        self.assertEqual(len(l1), 0)

        # user 1 wants to see wings of user 3 => 1 wing
        r = c.get('/api/v1/profiles/'+str(self.profile3.pk)+'/wings', HTTP_X_AUTH_TOKEN=self.token1, content_type='application/json')
        self.assertEqual(json.loads(r.content)['code'], 200)
        self.assertEqual(json.loads(r.content)['msg'], "Wings retrieved successfully.")
        self.assertEqual(json.loads(r.content)['status'], True)
        l1 = json.loads(r.content)['data']
        self.assertEqual(len(l1), 1)
        aux = {}
        aux['name'] = self.a3.name
        aux['id'] = self.a3.id
        aux['wingType'] = "Accommodation"
        self.assertEqual(l1[0], aux)


        # check that user 2 sees the same list as user 1 when looking for wings of user 3
        r = c.get('/api/v1/profiles/'+str(self.profile3.pk)+'/wings', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
        self.assertEqual(json.loads(r.content)['code'], 200)
        self.assertEqual(json.loads(r.content)['msg'], "Wings retrieved successfully.")
        self.assertEqual(json.loads(r.content)['status'], True)
        l2 = json.loads(r.content)['data']
        self.assertEqual(l1, l2)

        # user 2 wants to see wings of user 1 => 2 wings
        r = c.get('/api/v1/profiles/'+str(self.profile1.pk)+'/wings', HTTP_X_AUTH_TOKEN=self.token2, content_type='application/json')
        self.assertEqual(json.loads(r.content)['code'], 200)
        self.assertEqual(json.loads(r.content)['msg'], "Wings retrieved successfully.")
        self.assertEqual(json.loads(r.content)['status'], True)
        l1 = json.loads(r.content)['data']
        self.assertEqual(len(l1), 2)
        l = []
        aux = {}
        aux[unicode('name')] = unicode(self.a1.name)
        aux[unicode('id')] = int(self.a1.pk)
        aux[unicode('wingType')] = unicode("Accommodation")
        l.append(aux)
        aux2 = {}
        aux2[unicode('name')] = unicode(self.a2.name)
        aux2[unicode('id')] = int(self.a2.pk)
        aux2[unicode('wingType')] = unicode("Accommodation")
        l.append(aux2)
        self.assertEqual(l, l1)
