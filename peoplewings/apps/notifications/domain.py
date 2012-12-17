from django.db import models
import json
from peoplewings.apps.notifications.models import USERSTATE_CHOICES, TYPE_CHOICES

class NotificationsList(object):
    ## Notif specific
    id = models.IntegerField()
    created = models.CharField() # PASAR A TIMESTAMP!!
    read = models.BooleanField()
    kind = models.CharField()
    ## Request/inv specific
    state = models.CharField(choices = TYPE_CHOICES, default='P')
    flag_direction = models.BooleanField()    
    start_date = models.DateField()
    end_date = models.DateField()
    num_people = models.IntegerField()
    message = models.TextField()
    ## Msg/req/inv specific
    content = models.TextField()
    #Profile specific
    interlocutor_id = models.CharField()
    name = models.CharField()
    med_avatar =  models.CharField()
    age = models.IntegerField()
    verified = models.BooleanField()
    location = models.TextField()
    connected = models.CharField(choices = USERSTATE_CHOICES, default = 'F');
    ## URLs
    thread_url = models.CharField()
    
    def jsonable(self):
        res = dict()
        for key, value in self.__dict__.items():            
            res[key] = value
        return res

class AccomodationRequestThread(object):
    ## Notif specific
    id  = models.IntegerField()
    sender = models.IntegerField()
    receiver = models.IntegerField()
    created = models.CharField()
    reference = models.CharField()
    read = models.BooleanField()
    kind = models.CharField()
    ## AccomodationRequest specific
    wing_name = models.CharField()
    wing_id = models.CharField()
    state = models.CharField()        
    start_date = models.DateField()
    end_date = models.DateField()
    num_people = models.IntegerField()
    transport = models.CharField()
    private_message = models.TextField()
    #Sender specific
    nameS = models.CharField()    
    ageS = models.IntegerField()
    verifiedS = models.BooleanField()
    locationS = models.TextField()
    friendsS = models.IntegerField()
    referencesS = models.IntegerField()
    med_avatarS =  models.CharField()
    small_avatarS = models.CharField()
    #Receiver specific
    nameR = models.CharField()    
    ageR = models.IntegerField()
    verifiedR = models.BooleanField()
    locationR = models.TextField()
    friendsR = models.IntegerField()
    referencesR = models.IntegerField()
    med_avatarR =  models.CharField()
    small_avatarR = models.CharField()

    def jsonable(self):
        res = dict()
        for key, value in self.__dict__.items():            
            res[key] = value
        return res

def ComplexHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        return json.JSONEncoder.default(self, obj)
    
