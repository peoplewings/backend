##API for Notifications
import json
import ast
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
		list_allowed_methods = ['post', 'get']
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
		return errors				
	def filter_get(self, request, filters, prof):
		for key, value in request.GET.items():
			if key == 'kind':
				if value == 'reqinv':
					filters = filters & Q(kind='requests')|Q(kind='invites')
				elif value == 'msg':
					  filters = filters & Q(kind='messages')
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
		filters = Q(receiver=prof)|Q(sender=prof)
		order_by = '-created'
		filters = self.filter_get(request, filters, prof)
		try:
			my_notifications = Notifications.objects.filter(filters).order_by('-created')
			for i in my_notifications:
				#if not i.reference in result_dict:
				aux = NotificationsList()
				aux.id = i.pk
				aux.created = i.created
				if (i.sender == prof):
					aux.read = True
				else:
					aux.read = i.read
				aux.kind = i.kind
				## Request specific
				if aux.kind == 'requests':
					req = Requests.objects.get(pk = i.pk)
					additional_list = i.get_subclass().all()		
					for additional in additional_list:
						aux.start_date = additional.start_date
						aux.end_date = additional.end_date
						aux.num_people = additional.num_people 
						add_class = additional.get_class_name() 
						aux.wing_type = add_class                             
					aux.message = req.wing.name
					aux.state = req.state
					if i.first_sender == prof:                           
						aux.flag_direction = True
					else:
						aux.flag_direction =   False                      
					## URL                        
					aux.thread_url = '%s%srequestthread/%s' % (settings.BACKEND_SITE, add_class, i.reference)
					## Invite specific               
				elif aux.kind == 'invites':
					inv = Invites.objects.get(pk = i.pk) 
					additional_list = i.get_subclass().all()
					for additional in additional_list:
						aux.start_date = additional.start_date
						aux.end_date = additional.end_date
						aux.num_people = additional.num_people  
						add_class = additional.get_class_name()   
						aux.wing_type = add_class                                                                            
					aux.message = inv.wing.name
					aux.state = inv.state   
					if i.first_sender == prof.pk:
						 aux.flag_direction = True
					else:
						aux.flag_direction =   False          
					## URL
					aux.thread_url = '%s%sinvitethread/%s' % (settings.BACKEND_SITE, add_class, i.reference)
				## Message specific                         
				elif aux.kind == 'messages':					
					msg = Messages.objects.get(pk = i.pk)
					aux.content = msg.private_message
					## URL
					aux.thread_url = '%smessagethread/%s' % (settings.BACKEND_SITE, i.reference)
				## Friendship specific                         
				elif aux.kind == 'friendship':
					friend = Friendship.objects.get(pk = i.pk)
					aux.content = friend.message
					## URL
					aux.thread_url = '%sfriendthread/%s' % (settings.BACKEND_SITE, i.reference)
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
				else: aux.location = "Not specified, not specified, not specified"
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
			if o.thread_url not in [r.thread_url for r in result]:
				result.append(o)

		page_size=2
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
		POST = ast.literal_eval(request.raw_post_data)
		if 'kind' not in POST: return self.create_response(request, {"status":False, "errors":{"kind": ["This field is required"]}, "code":410}, response_class = HttpResponse)

		errors = self.validate(POST['kind'], POST)
		if len(errors.keys()) > 0:
			return self.create_response(request, {"status":False, "errors": errors, "code":410}, response_class = HttpResponse)
		# Create the notification
		try:
			if POST['kind'] == 'message':
				Notifications.objects.create_message(receiver = POST['idReceiver'], sender = request.user, content = POST['data']['content'])
		except Exception, e:
			return self.create_response(request, {"status":False, "errors": "The receiver of the message does not exists", "code":403}, response_class = HttpResponse)

		return self.create_response(request, {"status":True, "data":"The message has been sent succesfully", "code":200}, response_class = HttpResponse)
	
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



