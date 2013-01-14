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
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpMethodNotAllowed, HttpForbidden
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
		errors = {}
		if kind == 'message':
			#Messages need idReceiver and data. data needs content and content cannot be empty
			try:
				if POST['idReceiver'] is not None and POST['idReceiver'] == "": errors['idReceiver'] = 'This field cannot be empty'
			except KeyError:
				errors['idReceiver'] = 'This field is needed'
			try:
				if POST['data'] is not None and POST['data'] == "": errors['data'] = 'This field cannot be empty'
			except KeyError:
				errors['data'] = 'This field is needed'
			try:
				if POST['data']['content'] is not None and POST['data']['content']  == "": errors['content']  = 'The message cannot be empty'
				elif POST['data']['content'] is not None and len(POST['data']['content'])  > 1500: errors['content']  = 'The message is too long'
			except KeyError:
				errors['content']  = 'This field is needed'
		if kind == 'request':
			#Request need idReceiver and data. data needs content and content cannot be empty
			try:
				if POST['idReceiver'] is not None and POST['idReceiver'] == "": errors['idReceiver'] = 'This field cannot be empty'
			except KeyError:
				errors['idReceiver'] = 'This field is needed'
			try:
				if POST['data'] is not None and POST['data'] == "": errors['data'] = 'This field cannot be empty'
			except KeyError:
				errors['data'] = 'This field is needed'
			try:
				if POST['data']['privateText'] is not None and POST['data']['privateText']  == "": errors['privateText']  = 'The request private message cannot be empty'
				elif POST['data']['privateText'] is not None and len(POST['data']['privateText'])  > 1500: errors['privateText']  = 'The request private message is too long'
			except KeyError:
				errors['content']  = 'This field is needed'
			try:
				if POST['data']['publicText'] is not None and POST['data']['publicText']  == "": errors['publicText']  = 'The request public message cannot be empty'
				elif POST['data']['publicText'] is not None and len(POST['data']['publicText'])  > 1500: errors['publicText']  = 'The request public message is too long'
			except KeyError:
				errors['content']  = 'This field is needed'
			try:
				if POST['data']['wingParameters']['startDate'] > POST['data']['wingParameters']['endDate']: errors['endDate'] = 'This field should be greater or equal than the starting date'	
			except:
				errors['startDate'] = 'This field is needed'
				errors['endDate'] = 'This field is needed'	
		if kind == 'invite':
			#Invites need idReceiver and data. data needs content and content cannot be empty
			try:
				if POST['idReceiver'] is not None and POST['idReceiver'] == "": errors['idReceiver'] = 'This field cannot be empty'
			except KeyError:
				errors['idReceiver'] = 'This field is needed'
			try:
				if POST['data'] is not None and POST['data'] == "": errors['data'] = 'This field cannot be empty'
			except KeyError:
				errors['data'] = 'This field is needed'
			try:
				if POST['data']['privateText'] is not None and POST['data']['privateText']  == "": errors['privateText']  = 'The request private message cannot be empty'
				elif POST['data']['privateText'] is not None and len(POST['data']['privateText'])  > 1500: errors['privateText']  = 'The request private message is too long'
			except KeyError:
				errors['content']  = 'This field is needed'
			try:
				if POST['data']['wingParameters']['startDate'] > POST['data']['wingParameters']['endDate']: errors['endDate'] = 'This field should be greater or equal than the starting date'	
			except:
				errors['startDate'] = 'This field is needed'
				errors['endDate'] = 'This field is needed'	
		return errors		

	def put_list_validate(self, PUT, user):
		errors = {}
		if not PUT.has_key('threads'):
			errors['threads'] = "This field is required"
			return errors
		else:		
			#We check, for each thread, if they are owned by the user
			for i in PUT['threads']:
				try:
					notif = Notifications.objects.get(reference = i)
				except:
					notif = None
				if notif is not None:
					if (notif.receiver != user and notif.sender != user):
						errors[notif.reference] = "This reference is not owned by the user thus it can't be deleted"
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
					aux_dict_small = [o.thread_url for o in result_dict if o.search(k)]
					aux_dict_extended = [o for o in result_dict if o.thread_url in aux_dict_small]
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

	def get_list(self, request, **kwargs):		
		## We are doin it the hard way
		try:
			prof = UserProfile.objects.get(user = request.user)
		except:
			return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)
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
						aux.start_date = additional.start_date
						aux.end_date = additional.end_date
						aux.num_people = additional.num_people 
						add_class = additional.get_class_name() 
						aux.wing_type = add_class                             
					aux.message = '%s (%s in %s)' % (req.wing.name, req.wing.get_class_name(), req.wing.city.name)
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
						aux.start_date = additional.start_date
						aux.end_date = additional.end_date
						aux.num_people = additional.num_people  
						add_class = additional.get_class_name()   
						aux.wing_type = add_class                                                                            
					aux.message = '%s (%s in %s)' % (inv.wing.name, inv.wing.get_class_name(), inv.wing.city.name)
					aux.state = inv.state   
					if i.first_sender == prof.pk:
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

				aux.connected = 'F'
				## Add the result                                                                     
				result_dict.append(aux)                
		except Exception, e:
			raise e
			#return self.create_response(request, {"status":False, "msg":e, "code":"403"}, response_class = HttpResponse)   
		result = []
		#Here we will apply search filter and order_by		
		result_dict = self.search(request, result_dict)
		result_dict = self.order_by(request, result_dict)
		for o in result_dict:
			if o.reference not in [r.reference for r in result]:
				result.append(o)
		page_size=50
		num_page = int(request.GET.get('page', 1))
		count = len(result)
		endResult = min(num_page * page_size, count)
		startResult = min((num_page - 1) * page_size + 1, endResult)
		paginator = Paginator(result, page_size)
		
		try:
			page = paginator.page(num_page)
		except InvalidPage:
			return self.create_response(request, {"msg":"Sorry, no results on that page.", "code":413, "status":False}, response_class=HttpForbidden)    
		data = {}
		data["items"] = [i.jsonable() for i in page.object_list]
		data["count"] = count
		data["startResult"] = startResult
		data["endResult"] = endResult
		return self.create_response(request, {"status":True, "msg":"OK", "data" : data, "code":200}, response_class = HttpResponse)
					  	

	def post_list(self, request, **kwargs):
		##check if the request has the mandatory parameters
		POST = json.loads(request.raw_post_data)
		if 'kind' not in POST: return self.create_response(request, {"status":False, "errors":{"kind": ["This field is required"]}, "code":410}, response_class = HttpResponse)

		errors = self.validate(POST['kind'], POST)
		if len(errors.keys()) > 0:
			return self.create_response(request, {"status":False, "errors": errors, "code":410}, response_class = HttpResponse)
		# Create the notification
		
		if POST['kind'] == 'message':
			try:
				Notifications.objects.create_message(receiver = POST['idReceiver'], sender = request.user, content = POST['data']['content'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": "The receiver of the message does not exists", "code":403}, response_class = HttpResponse)
			return self.create_response(request, {"status":True, "data":"The message has been sent succesfully", "code":200}, response_class = HttpResponse)
		elif POST['kind'] == 'request':
			#Check that the receiver exists
			try:
				check_receiver = UserProfile.objects.get(pk = POST['idReceiver'])
			except:
				return self.create_response(request, {"status":False, "errors": "The receiver of the request does not exists", "code":403}, response_class = HttpResponse)
			#Check that the wing we entered is owned by the receiver
			try:
				check_wing = Wing.objects.get(pk = POST['data']['wingParameters']['wingId'])
				if check_wing.author.pk != POST['idReceiver']:
					return self.create_response(request, {"status":False, "errors": "The selected wing is not a valid choice", "code":410}, response_class = HttpResponse)
			except:	
				errors = {}
				errors['wingId'] = 'This field is required'
				return self.create_response(request, {"status":False, "errors": errors, "code":410}, response_class = HttpResponse)									
			try:
				notif = Notifications.objects.create_request(receiver = POST['idReceiver'], sender = request.user, wing = POST['data']['wingParameters']['wingId'], 
										private_message = POST['data']['privateText'], public_message = POST['data']['publicText'], 
										make_public = POST['data']['makePublic'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": e, "code":500}, response_class = HttpResponse)
			#create the additional info related with the request
			if (POST['data']['wingType'] == 'accomodation'):
				AccomodationInformation.objects.create_request(notification = notif, start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], 
											num_people = POST['data']['wingParameters']['capacity'], transport = POST['data']['wingParameters']['arrivingVia'], 
											flexible_start = POST['data']['wingParameters']['flexibleStart'], flexible_end = POST['data']['wingParameters']['flexibleEnd'])

			if POST['data']['makePublic'] is True:
				#we have to create a new wing...
				pass
				#TODO
			return self.create_response(request, {"status":True, "data":"The request has been sent succesfully", "code":200}, response_class = HttpResponse)
		elif POST['kind'] == 'invite':
			#Check that the receiver exists
			try:
				check_receiver = UserProfile.objects.get(pk = POST['idReceiver'])
			except:
				return self.create_response(request, {"status":False, "errors": "The receiver of the request does not exists", "code":403}, response_class = HttpResponse)
			#Check that the wing we entered is owned by the sender
			try:
				check_wing = Wing.objects.get(pk = POST['data']['wingParameters']['wingId'])
				if check_wing.author.pk != request.user.pk:
					return self.create_response(request, {"status":False, "errors": "The selected wing is not a valid choice", "code":410}, response_class = HttpResponse)
			except:	
				errors = {}
				errors['wingId'] = 'This field is required'
				return self.create_response(request, {"status":False, "errors": errors, "code":410}, response_class = HttpResponse)									
			try:
				notif = Notifications.objects.create_invite(receiver = POST['idReceiver'], sender = request.user, wing = POST['data']['wingParameters']['wingId'], private_message = POST['data']['privateText'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": e, "code":500}, response_class = HttpResponse)
			#create the additional info related with the request
			if (POST['data']['wingType'] == 'accomodation'):
				AccomodationInformation.objects.create_invite(notification = notif, start_date = POST['data']['wingParameters']['startDate'], end_date = POST['data']['wingParameters']['endDate'], 
											num_people = POST['data']['wingParameters']['capacity'], flexible_start = POST['data']['wingParameters']['flexibleStart'], 
											flexible_end = POST['data']['wingParameters']['flexibleEnd'])

			return self.create_response(request, {"status":True, "data":"The request has been sent succesfully", "code":200}, response_class = HttpResponse)
		else:
			return self.create_response(request, {"status":False, "data":"Not implemented", "code":400}, response_class = HttpResponse)

	def put_list(self, request, **kwargs):
		#This call comes from the DELETE
		profile = UserProfile.objects.get(user = request.user)
		PUT = json.loads(request.raw_post_data)
		errors = self.put_list_validate(PUT, profile)
		if len(errors.keys()) > 0:
			return self.create_response(request, {"status":False, "errors":errors, "code":400}, response_class = HttpResponse)
		#We have this shit validated, let's move on		
		refs = PUT["threads"]
		for i in refs:
			Notifications.objects.invisible_notification(i, profile)
		return self.create_response(request, {"status":True, "data": "The notifications have been deleted succesfully", "code":200}, response_class = HttpResponse)
	
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

	def validate(self, POST):
		errors = {}		
		if not POST.has_key('reference'):
			errors['reference']= 'This field is required'

		if not POST.has_key('kind'):
			errors['reference']= 'This field is not valid'

		if not POST.has_key('data'):
			errors['data'] = 'This field is required'
		else:
			if POST['kind'] not in ['request', 'invite', 'message']:
				errors['kind'] = 'This field is not valid'

		if POST.has_key('kind') and POST['kind'] == 'message' and POST.has_key('data'):
			if not POST['data'].has_key('content'):
				errors['content']= 'This field is required'
			else:
				if len(POST['data']['content']) > 1500:
					return "The message of the notification is too long"
				elif len(POST['data']['content']) == 0:
					return "The message of the notification cannot be empty"
		return errors

	def get_detail(self, request, **kwargs):
		ref = kwargs['pk']
		filters = Q(reference= ref)
		aux_list = []
		me = UserProfile.objects.get(user = request.user)

		notifs = Notifications.objects.filter(filters).order_by('created')
		if not notifs:
			return self.create_response(request, {"status":False, "errors":"The notification with that reference does not exists", "code":400}, response_class = HttpResponse)
		for i in notifs:
			if (i.sender.pk != me.pk and i.receiver.pk != me.pk):
				return self.create_response(request, {"status":False, "errors":"You are not allowed to visualize the notification with that reference", "code":400}, response_class = HttpResponse)			
			if i.kind == 'message':
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
				aux.sender_connected = 'F'
				#receiver info
				aux.receiver_id = i.receiver.pk
				aux.receiver_avatar = i.receiver.thumb_avatar
				#message info
				msg = Messages.objects.get(pk = i.pk)
				aux.content['message'] = msg.private_message
				#generic info
				aux.kind = i.kind
				aux.created = i.created
				aux.reference = i.reference
				aux.id = i.pk
			else:
				return self.create_response(request, {"status":False, "errors":"The notification with that reference does not exists", "code":400}, response_class = HttpResponse)
			#Once we filled the aux object, we have to add it to the list
			aux_list.append(aux.jsonable())
		#Now we have the list
		return self.create_response(request, {"status":True, "data": aux_list, "code":200}, response_class = HttpResponse)

	def post_list(self, request, **kwargs):
		POST = json.loads(request.raw_post_data)
		errors = self.validate(POST)
		me = UserProfile.objects.get(user= request.user)
		if isinstance(errors, dict) and len(errors.keys()) > 0:		
			return self.create_response(request, {"status":False, "errors": errors, "code":410}, response_class = HttpResponse)
		elif isinstance(errors, str):
			return self.create_response(request, {"status":False, "errors": errors, "code":400}, response_class = HttpResponse)
		try:
			notif = Notifications.objects.filter(reference= POST['reference'])[0]
			if not notif.receiver == me and not notif.sender == me:
				return self.create_response(request, {"status":False, "errors": "You are not permitted to respond in a thread that is not yours", "code":400}, response_class = HttpResponse)
		except Exception, e:
			return self.create_response(request, {"status":False, "errors": "The requested message does not exists", "code":400}, response_class = HttpResponse)
		#Get the receiver of the notification
		try:
			aux = Notifications.objects.filter(reference= POST['reference'])[0]
		except:
			return self.create_response(request, {"status":False, "errors": e, "code":403}, response_class = HttpResponse)
		if aux.receiver == me:
			receiver = aux.sender
		else:
			receiver = aux.receiver
		# Respond the notification
		if POST['kind'] == 'message':
			try:				
				Notifications.objects.respond_message(receiver = receiver.pk, sender = request.user, content = POST['data']['content'], reference= POST['reference'])
			except Exception, e:
				return self.create_response(request, {"status":False, "errors": e, "code":403}, response_class = HttpResponse)

		return self.create_response(request, {"status":True, "data": "Message sent succesfully", "code":200}, response_class = HttpResponse) 

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


