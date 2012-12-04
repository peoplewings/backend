from django.db import models
import json
#from peoplewings.libs.bussines import BussinesModel

class NotificationsList(object):
    ## Notif specific
    sender = models.IntegerField()
    receiver = models.IntegerField()
    created = models.CharField()
    reference = models.CharField()
    read = models.BooleanField()
    kind = models.CharField()
    ## Request/inv specific
    title = models.CharField()
    state = models.CharField()    
    start_date = models.DateField()
    end_date = models.DateField()
    num_people = models.IntegerField()
    ## Msg/req/inv specific
    private_message = models.TextField()
    #Profile specific
    med_avatar =  models.CharField()
    age = models.IntegerField()
    verified = models.BooleanField()
    location = models.TextField()
    
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
    
