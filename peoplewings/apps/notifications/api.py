##API for Notifications
import json
import pprint
from tastypie import http
from operator import itemgetter, attrgetter

from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpMethodNotAllowed
from tastypie.utils import trailing_slash
from tastypie.utils import dict_strip_unicode_keys

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.utils.cache import patch_cache_control
from django.contrib.auth.models import User
from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage

from peoplewings.apps.people.models import UserProfile
from wings.models import Wing
from models import Notifications, Requests, Invites, Messages, NotificationsAlarm, AdditionalInformation, AccomodationInformation, Friendship

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.libs.bussines import *
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

from domain import *

class NotificationsListResource(ModelResource):
	
	class Meta:
		object_class = Notifications
		queryset = Notifications.objects.all()
		detail_allowed_methods = []
		list_allowed_methods = ['post', 'get', 'put']
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True     
		resource_name = 'notificationslist'               

	def validate(self, kind, POST):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		if kind == 'message':
			#Messages need idReceiver and data. data needs content and content cannot be empty
			try:
				if POST['idReceiver'] is not None and POST['idReceiver'] == "": not_empty['extras'].append('idReceiver')
			except KeyError:
				field_req['extras'].append('idReceiver')
			try:
				if POST['data'] is not None and POST['data'] == "": not_empty['extras'].append('data')
			except KeyError:
				field_req['extras'].append('data')
			try:
				if POST['data']['content'] is not None and POST['data']['content']  == "": not_empty['extras'].append('content')
				elif POST['data']['content'] is not None and len(POST['data']['content'])  > 1500: too_long['extras'].append('content')
			except KeyError:
				field_req['extras'].append('content')
		if kind == 'request':
			#Request need idReceiver and data. data needs content and content cannot be empty
			try:
				if POST['idReceiver'] is not None and POST['idReceiver'] == "": not_empty['extras'].append('idReceiver')
			except KeyError:
				field_req['extras'].append('idReceiver')
			try:
				if POST['data'] is not None and POST['data'] == "": not_empty['extras'].append('data')
			except KeyError:
				field_req['extras'].append('data')
			try:
				if POST['data']['privateText'] is not None and POST['data']['privateText']  == "": not_empty['extras'].append('privateText')
				elif POST['data']['privateText'] is not None and len(POST['data']['privateText'])  > 1500: too_long['extras'].append('privateText')
			except KeyError:
				field_req['extras'].append('privateText')
			try:
				if POST['data']['publicText'] is not None and POST['data']['publicText']  == "": not_empty['extras'].append('publicText')
				elif POST['data']['publicText'] is not None and len(POST['data']['publicText'])  > 1500: too_long['extras'].append('publicText')
			except KeyError:
				field_req['extras'].append('publicText')
			try:
				if POST['data'] is not None and POST['data'] == "": not_empty['extras'].append('data')
			except KeyError:
				field_req['extras'].append('data')
			try:
				if POST['data']['wingParameters']['startDate'] > POST['data']['wingParameters']['endDate']: errors.append({"type":"START_DATE_GT_END_DATE"})
			except:
				field_req['extras'].append('startdate')
				field_req['extras'].append('endDate')
		if kind == 'invite':
			#Invites need idReceiver and data. data needs content and content cannot be empty
			try:
				if POST['idReceiver'] is not None and POST['idReceiver'] == "": not_empty['extras'].append('idReceiver')
			except KeyError:
				field_req['extras'].append('idReceiver')
			try:
				if POST['data'] is not None and POST['data'] == "": not_empty['extras'].append('data')
			except KeyError:
				field_req['extras'].append('data')
			try:
				if POST['data']['privateText'] is not None and POST['data']['privateText']  == "": not_empty['extras'].append('privateText')
				elif POST['data']['privateText'] is not None and len(POST['data']['privateText'])  > 1500: too_long['extras'].append('privateText')
			except KeyError:
				field_req['extras'].append('privateText')
			try:
				if POST['data']['wingParameters']['startDate'] > POST['data']['wingParameters']['endDate']: errors.append({"type":"START_DATE_GT_END_DATE"})	
			except:
				field_req['extras'].append('startdate')
				field_req['extras'].append('endDate')	
		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		return errors		

	def put_list_validate(self, PUT, user):
		errors = []
		if not PUT.has_key('threads'):
			errors.append({"type": "FIELD_REQUIRED", "extra":["threads"]})
			return errors
		else:		
			#We check, for each thread, if they are owned by the user
			err = {"type":"FORBIDDEN", "extras":[]}
			for i in PUT['threads']:
				try:
					notif = Notifications.objects.get(reference = i)
				except:
					notif = None
				if notif is not None:
					if (notif.receiver != user and notif.sender != user):
						err['extras'].append(i)
			if len(err['extras']) > 0:
				errors.append(err)
		return errors

	def filter_get(self, request, filters, prof):
		for key, value in request.GET.items():
			if key == 'kind':
				if value == 'reqinv':
					filters = filters & Q(kind='request')|Q(kind='invite')
				elif value == 'msg':
					  filters = filters & Q(kind='message')
				elif value == 'friendship':
					  filters = filters & Q(kind='friends')
			elif key == 'target':
				if value == 'received':
					filters = filters & ~Q(first_sender = prof)
				elif value == 'sent':
					filters = filters & Q(first_sender = prof)
			elif key == 'state' and 'kind' in request.GET.keys() and 'reqinv' == request.GET['kind']:
				#Filtro por estado de la request
				filters = filters & (Q(requests__state = value) | Q(invites__state = value)) 
		return filters

	def search(self, request, initial_dict):
		result_dict = []
		result_dict.extend(initial_dict)
		for key, value in request.GET.items():
			if key == 'search':
				list_value = value.split(' ')
				search_list = []

				for k in list_value:
					#We search within each notification (domain) if the element has the value
					aux_dict_small = [o.reference for o in result_dict if o.search(k)]
					#We put all the notifications where the reference is in aux_dict_small in another list
					aux_dict_extended = [o for o in result_dict if o.reference in aux_dict_small]
					search_list += aux_dict_extended
				return search_list
		return result_dict

	def order_by(self, request, initial_dict):
		result_dict = []
		result_dict.extend(initial_dict)
		for key, value in request.GET.items():			
			if key == 'order':
				if  value == 'date':
					 result_dict = sorted(result_dict, key=attrgetter('created'), reverse=True)
				elif value == 'interlocutor':                                        
					result_dict = sorted(result_dict, key=attrgetter('name'), reverse=False)
				elif value == 'read':
					result_dict = sorted(result_dict, key=attrgetter('read'), reverse=False)
				elif value == 'date-start' and 'reqinv' in [val for key, val in request.GET.items() if key == 'kind']:
					result_dict = sorted(result_dict, key=attrgetter('start_date'), reverse=True)
				elif value == 'type' and 'reqinv' in [val for key, val in request.GET.items() if key == 'kind']:
					result_dict = sorted(result_dict, key=attrgetter('wing_type'), reverse=True)
		return result_dict

	def make_difs_individual(self, first, second):
		mod = []
		if first.wing_parameters.has_key('start_date') and second.wing_parameters.has_key('start_date') and not first.wing_parameters['start_date'] == second.wing_parameters['start_date']:
			mod.append('startDate')
		if first.wing_parameters.has_key('end_date') and second.wing_parameters.has_key('end_date') and not first.wing_parameters['end_date'] == second.wing_parameters['end_date']:
			mod.append('endDate')
		if first.wing_parameters.has_key('num_people') and second.wing_parameters.has_key('num_people') and not first.wing_parameters['num_people'] == second.wing_parameters['num_people']:
			mod.append('numPeople')
		return mod

	def make_difs(self, thread, me):
		mod = []
		for idx, i in enumerate(thread):			
			if i.sender == me:
				break
			else:
				if len(thread) > idx+1:
					mod = mod + self.make_difs_individual(i, thread[idx+1])

		thread[0].wing_parameters['modified'] = mod
		return thread

	def connected(self, user):
		state = 'OFF'
		token = ApiToken.objects.filter(user=user).order_by('-last_js')
		if len(token) > 0:
			state = token[0].is_user_connected()	
		return state

	def get_list(self, request, **kwargs):		
		## We are doin it the hard way
		try:
			prof = UserProfile.objects.get(user = request.user)
		except:
			return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['user']}]}, response_class = HttpResponse)
		result_dict = []     
		filters = (Q(receiver=prof)|Q(sender=prof))&((Q(first_sender=prof)&Q(first_sender_visible=True))|(~Q(first_sender=prof)&Q(second_sender_visible=True)))
		order_by = '-created'
		filters = self.filter_get(request, filters, prof)
		try:
			my_notifications = Notifications.objects.filter(filters).order_by('-created')
			for i in my_notifications:				
				aux = NotificationsList()
				aux.id = i.pk
				aux.created = i.created
				aux.reference = i.reference
				if (i.sender == prof):
					aux.read = True
				else:
					aux.read = i.read
				aux.kind = i.kind
				## Request specific
				if aux.kind == 'request':
					req = Requests.objects.get(pk = i.pk)
					additional_list = i.get_subclass().all()		
					for additional in additional_list:
						aux.wing_parameters['start_date'] = additional.start_date
						aux.wing_parameters['end_date'] = additional.end_date
						aux.wing_parameters['num_people'] = additional.num_people 
						add_class = additional.get_class_name() 
						aux.wing_parameters['wing_type'] = add_class
						aux.wing_parameters['wing_city'] = req.wing.city.name                           
					aux.wing_parameters['message'] = req.wing.name
					aux.state = req.state
					if i.first_sender == prof:                           
						aux.flag_direction = True
					else:
						aux.flag_direction =   False           					                            
				## Invite specific               
				elif aux.kind == 'invite':
					inv = Invites.objects.get(pk = i.pk) 
					additional_list = i.get_subclass().all()		
					for additional in additional_list:
						aux.wing_parameters['start_date'] = additional.start_date
						aux.wing_parameters['end_date'] = additional.end_date
						aux.wing_parameters['num_people'] = additional.num_people 
						add_class = additional.get_class_name() 
						aux.wing_parameters['wing_type'] = add_class
						aux.wing_parameters['wing_city'] = inv.wing.city.name                           
					aux.wing_parameters['message'] = inv.wing.name
					aux.state = inv.state   
					if i.first_sender == prof:
						 aux.flag_direction = True
					else:
						aux.flag_direction =   False          
				## Message specific                         
				elif aux.kind == 'message':					
					msg = Messages.objects.get(pk = i.pk)
					aux.content = msg.private_message
				## Friendship specific                         
				elif aux.kind == 'friendship':
					friend = Friendship.objects.get(pk = i.pk)
					aux.content = friend.message
				#Profile specific
				if (i.sender == prof):
					## YOU are the sender. Need receiver info
					prof_aux = UserProfile.objects.get(pk = i.receiver.pk)                   
				else:
					## YOU are the receiver. Need the sender info  
					prof_aux = UserProfile.objects.get(pk = i.sender.pk)     
				aux.interlocutor_id = prof_aux.pk          
				aux.avatar =  prof_aux.thumb_avatar
				aux.age = prof_aux.get_age()
				aux.verified = False         
				if prof_aux.current_city: aux.location = prof_aux.current_city.stringify()
				else: aux.location = "Not specified"
				aux.name = '%s %s' % (prof_aux.user.first_name, prof_aux.user.last_name)
				aux.online = self.connected(prof_aux.user)
				## Add the result                                                                     
				result_dict.append(aux)                
		except Exception, e:
			return self.create_response(request, {"status":False, "errors": [{"type":"INTERNAL_ERROR"}]}, response_class = HttpResponse)
			#return self.create_response(request, {"status":False, "msg":e, "code":"403"}, response_class = HttpResponse)
		result = {}
		result_idx = []
		#Here we will apply search filter and order_by		
		result_dict = self.search(request, result_dict)
		result_dict = self.order_by(request, result_dict)
		for o in result_dict:
			if o.reference not in result.keys():				
				result[o.reference] = [o]
				result_idx.append(o.reference)
			else:
				result[o.reference].append(o)
		for o in result.keys():
			o = self.make_difs(result[o], prof)

		final_result = []
		for i in result_idx:
			final_result.append(result[i][0])
		page_size=50
		num_page = int(request.GET.get('page', 1))
		count = len(result)
		endResult = min(num_page * page_size, count)
		startResult = min((num_page - 1) * page_size + 1, endResult)
		paginator = Paginator(final_result, page_size)
		
		try:
			page = paginator.page(num_page)
		except InvalidPage:
			return self.create_response(request, {"status":False, "errors": [{"type":"NO_CONTENT"}]}, response_class = HttpResponse)
		data = {}
		data["items"] = [i.jsonable() for i in page.object_list]
		data["count"] = count
		data["startResult"] = startResult
		data["endResult"] = endResult
		return self.create_response(request, {"status":True, "data" : data}, response_class = HttpResponse)
					  	

	def post_list(self, request, **kwargs):
		##check if the request has the mandatory parameters
		POST = json.loads(request.raw_post_data)
		if 'kind' not in POST: return self.create_response(request, {"status":False, "errors":[{"type":"FIELD_REQUIRED", "extras":["kind"]}]}, response_class = HttpResponse)

		errors = self.validate(POST['kind'], POST)
		if len(errors) > 0:
			return self.create_response(request, {"status":False, "errors": errors}, response_class = HttpResponse)
		# Create the notification
		
		if POST['kind'] == 'message':
			try:
				Notifications.objects.create_message(receiver = POST['idReceiver'], sender = request.user, content = POST['data']['content'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['receiver']}]}, response_class = HttpResponse)
			return self.create_response(request, {"status":True}, response_class = HttpResponse)
		elif POST['kind'] == 'request':
			#Check that the receiver exists
			try:
				check_receiver = UserProfile.objects.get(pk = POST['idReceiver'])
			except:
				return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['receiver']}]}, response_class = HttpResponse)
			#Check that the wing we entered is owned by the receiver
			try:
				check_wing = Wing.objects.get(pk = POST['data']['wingParameters']['wingId'])
				if check_wing.author.pk != POST['idReceiver']:
					return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['wing']}]}, response_class = HttpResponse)
			except:	
				return self.create_response(request, {"status":False, "errors": [{"type":"FIELD_REQUIRED", "extras":["wingId"]}]}, response_class = HttpResponse)								
			try:
				notif = Notifications.objects.create_request(receiver = POST['idReceiver'], sender = request.user, wing = POST['data']['wingParameters']['wingId'], 
										private_message = POST['data']['privateText'], public_message = POST['data']['publicText'], 
										make_public = POST['data']['makePublic'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": [{"type":"INTERNAL_ERROR"}]}, response_class = HttpResponse)
			#create the additional info related with the request
			if (POST['data']['wingType'] == 'Accomodation'):
				AccomodationInformation.objects.create_request(notification = notif, start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], 
											num_people = POST['data']['wingParameters']['capacity'], transport = POST['data']['wingParameters']['arrivingVia'], 
											flexible_start = POST['data']['wingParameters']['flexibleStart'], flexible_end = POST['data']['wingParameters']['flexibleEnd'])

			if POST['data']['makePublic'] is True:
				#we have to create a new wing...
				pass
				#TODO
			return self.create_response(request, {"status":True}, response_class = HttpResponse)
		elif POST['kind'] == 'invite':
			#Check that the receiver exists
			try:
				check_receiver = UserProfile.objects.get(pk = POST['idReceiver'])
			except:
				return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['receiver']}]}, response_class = HttpResponse)
			#Check that the wing we entered is owned by the sender
			try:
				check_wing = Wing.objects.get(pk = POST['data']['wingParameters']['wingId'])
				if check_wing.author.pk != request.user.pk:
					return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['wing']}]}, response_class = HttpResponse)
			except:
				return self.create_response(request, {"status":False, "errors": [{"type":"FIELD_REQUIRED", "extras":["wingId"]}]}, response_class = HttpResponse)								
			try:
				notif = Notifications.objects.create_invite(receiver = POST['idReceiver'], sender = request.user, wing = POST['data']['wingParameters']['wingId'], private_message = POST['data']['privateText'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": [{"type":"INTERNAL_ERROR"}]}, response_class = HttpResponse)
			#create the additional info related with the request
			if (POST['data']['wingType'] == 'Accomodation'):
				AccomodationInformation.objects.create_invite(notification = notif, start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], 
											num_people = POST['data']['wingParameters']['capacity'], flexible_start = POST['data']['wingParameters']['flexibleStart'], 
											flexible_end = POST['data']['wingParameters']['flexibleEnd'])

			return self.create_response(request, {"status":True}, response_class = HttpResponse)
		else:
			return self.create_response(request, {"status":False, "errors": [{"type":"INVALID", "extras":['kind']}]}, response_class = HttpResponse)

	def put_list(self, request, **kwargs):
		#This call comes from the DELETE
		profile = UserProfile.objects.get(user = request.user)
		PUT = json.loads(request.raw_post_data)
		errors = self.put_list_validate(PUT, profile)
		if len(errors) > 0:
			return self.create_response(request, {"status":False, "errors":errors}, response_class = HttpResponse)
		#We have this shit validated, let's move on		
		refs = PUT["threads"]
		for i in refs:
			Notifications.objects.invisible_notification(i, profile)
		return self.create_response(request, {"status":True}, response_class = HttpResponse)
	
	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)              
				return response
			except (BadRequest, fields.ApiFieldError), e:
				return http.HttpBadRequest(e.args[0])
			except ValidationError, e:
				return http.HttpBadRequest(', '.join(e.messages))
			except Exception, e:
				if hasattr(e, 'response'):
					return e.response

				# A real, non-expected exception.
				# Handle the case where the full traceback is more helpful
				# than the serialized error.
				if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
					raise

				# Re-raise the error to get a proper traceback when the error
				# happend during a test case
				if request.META.get('SERVER_NAME') == 'testserver':
					raise

				# Rather than re-raising, we're going to things similar to
				# what Django does. The difference is returning a serialized
				# error message.
				return self._handle_500(request, e)

		return wrapper

class NotificationsThreadResource(ModelResource):
	
	class Meta:
		object_class = Notifications
		queryset = Notifications.objects.all()
		detail_allowed_methods = []
		list_allowed_methods = []
		detail_allowed_methods = ['get']
		list_allowed_methods = ['post']
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True     
		resource_name = 'notificationsthread'

	def make_options(self, me, thread):
		a = Automata()
		states = []
		options = {}
		for i in thread:
			states.append([i.state, i.sender.pk])
		first_sender = thread[0].first_sender
		states_copy = list(states)
		states_copy.append(['A', me.pk])
		can_accept = a.check_P(states_copy, first_sender)
		states_copy = list(states)
		states_copy.append(['M', me.pk])
		can_maybe = a.check_P(states_copy, first_sender)
		states_copy = list(states)
		states_copy.append(['D', me.pk])
		can_deny = a.check_P(states_copy, first_sender)
		states_copy = list(states)
		states_copy.append(['P', me.pk])
		can_pending = a.check_P(states_copy, first_sender)

		if can_accept is True:
			if states[len(states)-1][0] == 'A':
				options['canAccept'] = 'C'
			else:
				options['canAccept'] = 'T'
		else:
			options['canAccept'] = 'F'
		if can_maybe is True:
			if states[len(states)-1][0] == 'M':
				options['canMaybe'] = 'C'
			else:
				options['canMaybe'] = 'T'
		else:
			options['canMaybe'] = 'F'
		if can_deny is True:
			if states[len(states)-1][0] == 'D':
				options['canDeny'] = 'C'
			else:
				options['canDeny'] = 'T'
		else:
			options['canDeny'] = 'F'
		if can_pending is True:
			if states[len(states)-1][0] == 'P':
				options['canPending'] = 'C'
			else:
				options['canPending'] = 'T'
		else:
			options['canPending'] = 'F'
		return options


	def validate_post_list(self, POST):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		invalid = {"type":'INVALID', 'extras':[]}
		kind = None	
		if not POST.has_key('reference'):
			field_req['extras'].append('reference')
		else:
			notif = Notifications.objects.filter(reference=POST['reference'])
			if(len(notif) > 0):
				kind = notif[0].kind
			else: 
				invalid['extras'].append('reference')

		if not POST.has_key('data'):
			field_req['extras'].append('data')

		if kind and kind == 'message' and POST.has_key('data'):
			if not POST['data'].has_key('content'):
				field_req['extras'].append('content')
			else:
				if len(POST['data']['content']) > 1500:
					too_long['extras'].append('content')
				elif len(POST['data']['content']) == 0:
					not_empty['extras'].append('content')
		elif (kind == 'request' or kind == 'invite') and POST.has_key('data'):
			data = POST['data']
			start = None
			end = None
			if not data.has_key('content'):
				field_req['extras'].append('content')
			else:
				if data.has_key('content') and len(data['content']) > 1500:
					too_long['extras'].append('content')
				if data.has_key('content') and len(data['content']) == 0:
					not_empty['extras'].append('content')
			if data.has_key('state'): 
				if data['state'] not in ['P', 'A', 'M', 'D']:
					invalid['extras'].append('kind')
			else:
				field_req['extras'].append('state')
			if data.has_key('wingParameters'):
				params = data['wingParameters']
				if params.has_key('startDate') and isinstance(params['startDate'], int):
					start = params['startDate']
				else:
					field_req['extras'].append('startDate')
				if params.has_key('endDate') and isinstance(params['endDate'], int):
					end = params['endDate']
				else:
					field_req['extras'].append('endDate')
				if start > end:
					errors.append({"type":"START_DATE_GT_END_DATE"})
				if params.has_key('capacity'):
					if params['capacity'] == 0:
						invalid['extras'].append('capacity')
				else:
					field_req['extras'].append('capacity')
				if not params.has_key('flexibleStartDate'):
					field_req['extras'].append('flexibleStartDate')
				if not params.has_key('flexibleEndDate'):
					field_req['extras'].append('flexibleEndDate')
			else:
				field_req['extras'].append('wingParameters')
		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(invalid['extras']) > 0:
			errors.append(invalid)
		return errors

	def get_last_state_mod(self, thread, thread_len):
		curr = thread[thread_len-1].state
		cursor = 0
		thread_rev = [i for i in thread[::-1]]		
		for i in thread_rev:
			if not i.state == curr:
				return thread_rev[cursor-1].sender
			cursor = cursor + 1
		return None

	def make_difs_individual(self, first, second):
		mod = []
		first_ai = AccomodationInformation.objects.get(notification=first.pk)
		second_ai = AccomodationInformation.objects.get(notification=second.pk)

		if first_ai.start_date and second_ai.start_date and not first_ai.start_date == second_ai.start_date:
			mod.append('startDate')
		if first_ai.end_date and second_ai.end_date and not first_ai.end_date == second_ai.end_date:
			mod.append('endDate')
		if first_ai.num_people and second_ai.num_people and not first_ai.num_people == second_ai.num_people:
			mod.append('capacity')
		return mod

	def make_difs(self, me, req, kind):
		if kind == 'request':
			thread = Requests.objects.filter(reference = req.reference).order_by('-created')
		elif kind == 'invite':
			thread = Invites.objects.filter(reference = req.reference).order_by('-created')

		mod = []
		for idx, i in enumerate(thread):			
			if i.sender == me:
				break
			else:
				if len(thread) > idx+1:
					mod = mod + self.make_difs_individual(i, thread[idx+1])
		return mod


	def delete_alarms(self, ref, me):
		to_delete= NotificationsAlarm.objects.filter(reference = ref, receiver=me)
		for i in to_delete:
			i.delete()

	def connected(self, user):
		state = 'OFF'
		token = ApiToken.objects.filter(user=user).order_by('-last_js')
		if len(token) > 0:
			state = token[0].is_user_connected()
		return state

	def get_detail(self, request, **kwargs):
		ref = kwargs['pk']
		filters = Q(reference= ref)
		aux_list = []
		me = UserProfile.objects.get(user = request.user)

		notifs = Notifications.objects.filter(filters).order_by('created')
		if not notifs:
			return self.create_response(request, {"status":False, "errors":[{"type":"INVALID", "extras":['reference']}]}, response_class = HttpResponse)
		kind = None
		data = {}
		thread = []

		for i in notifs:
			if (i.sender.pk != me.pk and i.receiver.pk != me.pk):
				return self.create_response(request, {"status":False, "errors":[{"type":"FORBIDDEN", "extras":[ref]}]}, response_class = HttpResponse)			
			if i.kind == 'message':
				kind = 'message'
				aux = MessageThread()
				#sender info
				aux.sender_id = i.sender.pk
				aux.sender_name = '%s %s' % (i.sender.user.first_name, i.sender.user.last_name)
				aux.sender_age = i.sender.get_age()
				aux.sender_verified = True
				aux.sender_location = i.sender.current_city.stringify()
				aux.sender_friends = i.sender.relationships.count()
				aux.sender_references = i.sender.references.count()
				aux.sender_med_avatar = i.sender.medium_avatar
				aux.sender_small_avatar = i.sender.thumb_avatar
				aux.sender_online = self.connected(i.sender)
				#receiver info
				aux.receiver_id = i.receiver.pk
				aux.receiver_avatar = i.receiver.thumb_avatar
				#message info
				msg = Messages.objects.get(pk = i.pk)
				aux.content['message'] = msg.private_message
				#generic info				
				aux.created = i.created
			elif i.kind == 'request' or i.kind == 'invite':
				if i.kind == 'request':
					kind = 'request'
					req = Requests.objects.get(pk=i.pk)					
				else:
					kind = 'invite'
					req = Invites.objects.get(pk=i.pk)
				thread.append(req)
				aux = RequestItem()
				aux.senderId= i.sender.pk
				aux.senderName= '%s %s' % (i.sender.user.first_name, i.sender.user.last_name)
				aux.senderAge= i.sender.get_age()
				aux.senderVerified= True
				aux.senderLocation= i.sender.current_city.stringify()
				aux.senderFriends= i.sender.relationships.count()
				aux.senderReferences= i.sender.references.count()
				aux.senderMedAvatar= i.sender.medium_avatar
				aux.senderSmallAvatar= i.sender.thumb_avatar
				aux.senderOnline=  self.connected(i.sender)
				#receiver info
				aux.receiverId= i.receiver.pk
				aux.receiverAvatar= i.receiver.thumb_avatar
				#Contents info
				aux.content= {}
				if i.kind == 'request':
					aux.content['message'] = req.public_message + '\n' + req.private_message 
				else:
					aux.content['message'] = req.private_message 		
				#Generic info				
				aux.created= i.created
			else:
				return self.create_response(request, {"status":False, "errors":[{"type":"INVALID", "extras":['reference']}]}, response_class = HttpResponse)
			#Once we filled the aux object, we have to add it to the list
			if i.receiver.pk == me.pk:
				i.read = True
				i.save()
			aux_list.append(aux.jsonable())
		#Now we have the list
		if kind == 'message':
			data['items'] = aux_list
			data['kind'] = kind
			data['reference'] = ref
		elif kind == 'request' or kind == 'invite':
			data = RequestThread()
			data.reference = ref
			data.kind= kind
			data.firstSender= req.first_sender.pk	
			data.wing['type'] = req.wing.get_class_name()
			if req.state == 'X':
				state = 'D'
			else: 
				state = req.state
			data.wing['state'] = state
			data.wing['parameters']['wingId']= req.wing.pk
			data.wing['parameters']['wingName']= req.wing.name
			data.wing['parameters']['wingCity']= req.wing.city.name
			if req.wing.get_class_name() == 'Accomodation':
				data.wing['parameters']['startDate']= req.accomodationinformation_notification.get().start_date
				data.wing['parameters']['endDate']= req.accomodationinformation_notification.get().end_date
				data.wing['parameters']['capacity']= req.accomodationinformation_notification.get().num_people
				data.wing['parameters']['arrivingVia']= req.accomodationinformation_notification.get().transport
				data.wing['parameters']['flexibleStartDate']= req.accomodationinformation_notification.get().flexible_start
				data.wing['parameters']['flexibleEndDate']= req.accomodationinformation_notification.get().flexible_end
			data.wing['parameters']['modified'] = self.make_difs(me, req, data.kind)
			last_state_mod = self.get_last_state_mod(thread, len(thread))
			options = self.make_options(me, thread)
			if options['canAccept'] == 'T':
				data.options.append('Accept')
			elif options['canAccept'] == 'C':
				data.options.append('Chat')
			if options['canMaybe'] == 'T':
				data.options.append('Maybe')
			elif options['canMaybe'] == 'C':
				data.options.append('Chat')
			if options['canPending'] == 'T':
				data.options.append('Pending')
			elif options['canPending'] == 'C':
				data.options.append('Chat')
			if options['canDeny'] == 'T':
				data.options.append('Deny')
			elif options['canDeny'] == 'C':
				data.options.append('Chat')

			data.items = aux_list
			data = data.jsonable()
		else:
			data = {}

		self.delete_alarms(ref, me)
		return self.create_response(request, {"status":True, "data": data}, response_class = HttpResponse)

	def post_list(self, request, **kwargs):		
		POST = json.loads(request.raw_post_data)
		errors = self.validate_post_list(POST)
		arriving_via = None
		me = UserProfile.objects.get(user= request.user)
		if len(errors) > 0:
			return self.create_response(request, {"status":False, "errors": errors}, response_class = HttpResponse)
		kind = Notifications.objects.filter(reference=POST['reference'])[0].kind
		try:
			notif_list = Notifications.objects.filter(reference= POST['reference'])
			notif = notif_list[len(notif_list)-1]
			if not notif.receiver == me and not notif.sender == me:
				return self.create_response(request, {"status":False, "errors": [{"type":"FORBIDDEN", "extras":[POST['reference']]}]}, response_class = HttpResponse)
		except Exception, e:
			return self.create_response(request, {"status":False, "errors":[{"type":"INVALID", "extras":['reference']}]}, response_class = HttpResponse)

		#Get the receiver of the notification
		aux = notif_list[0]
		if aux.receiver == me:
			receiver = aux.sender
		else:
			receiver = aux.receiver
		# Respond the notification
		if kind == 'message':
			try:				
				Notifications.objects.respond_message(receiver = receiver.pk, sender = request.user, content = POST['data']['content'], reference= POST['reference'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": [{"type":"INTERNAL_ERROR"}]}, response_class = HttpResponse)

			return self.create_response(request, {"status":True}, response_class = HttpResponse) 
		if kind == 'request':
			try:	
				request_result = Notifications.objects.respond_request(reference = POST['reference'], receiver = receiver.pk, sender =me.pk, content = POST['data']['content'], state = POST['data']['state'], start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], flexible_start = POST['data']['wingParameters']['flexibleStartDate'], flexible_end= POST['data']['wingParameters']['flexibleEndDate'])
				if isinstance(request_result, str):
					return self.create_response(request, {"status":False, "errors": request_result, "code":400}, response_class = HttpResponse)
				if request_result.wing.get_class_name() == 'Accomodation':
					additional = AccomodationInformation.objects.get(notification = notif.pk)
					if (POST['data']['state']=='D'):
						AccomodationInformation.objects.create_request(notification = request_result, start_date = additional.start_date, end_date = additional.end_date, 
													num_people = additional.num_people, transport = additional.transport, 
													flexible_start = additional.flexible_start, flexible_end = additional.flexible_end)
					else:				
						AccomodationInformation.objects.create_request(notification = request_result, start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], 
													num_people = POST['data']['wingParameters']['capacity'], transport = additional.transport, 
													flexible_start = POST['data']['wingParameters']['flexibleStartDate'], flexible_end = POST['data']['wingParameters']['flexibleEndDate'])

			except Exception, e:
				return self.create_response(request, {"status":False, "errors": [{"type":"INTERNAL_ERROR"}]}, response_class = HttpResponse)
			return self.create_response(request, {"status":True}, response_class = HttpResponse)
		if kind == 'invite':
			try:				
				invite_result = Notifications.objects.respond_invite(reference = POST['reference'], receiver = receiver.pk, sender =me.pk, content = POST['data']['content'], state = POST['data']['state'], start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], flexible_start = POST['data']['wingParameters']['flexibleStartDate'], flexible_end= POST['data']['wingParameters']['flexibleEndDate'])
				if isinstance(invite_result, str):
					return self.create_response(request, {"status":False, "errors": invite_result, "code":400}, response_class = HttpResponse)
				if invite_result.wing.get_class_name() == 'Accomodation':
					additional = AccomodationInformation.objects.get(notification = notif.pk)
					if (POST['data']['state']=='D'):
						AccomodationInformation.objects.create_request(notification = invite_result, start_date = additional.start_date, end_date = additional.end_date, 
													num_people = additional.num_people, transport = additional.transport, 
													flexible_start = additional.flexible_start, flexible_end = additional.flexible_end)
					else:						
						AccomodationInformation.objects.create_invite(notification = invite_result, start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], 
													num_people = POST['data']['wingParameters']['capacity'], transport = additional.transport, 
													flexible_start = POST['data']['wingParameters']['flexibleStartDate'], flexible_end = POST['data']['wingParameters']['flexibleEndDate'])

			except Exception, e:
				return self.create_response(request, {"status":False, "errors": [{"type":"INTERNAL_ERROR"}]}, response_class = HttpResponse)
			return self.create_response(request, {"status":True}, response_class = HttpResponse)
		return self.create_response(request, {"status":False, "errors":[{"type":"INVALID", "extras":['kind']}]}, response_class = HttpResponse)

	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)
				return response
			except (BadRequest, fields.ApiFieldError), e:
				return http.HttpBadRequest(e.args[0])
			except ValidationError, e:
				return http.HttpBadRequest(', '.join(e.messages))
			except Exception, e:
				if hasattr(e, 'response'):
					return e.response

				# A real, non-expected exception.
				# Handle the case where the full traceback is more helpful
				# than the serialized error.
				if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
					raise

				# Re-raise the error to get a proper traceback when the error
				# happend during a test case
				if request.META.get('SERVER_NAME') == 'testserver':
					raise

				# Rather than re-raising, we're going to things similar to
				# what Django does. The difference is returning a serialized
				# error message.
				return self._handle_500(request, e)

		return wrapper


