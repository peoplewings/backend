from django.db import models
from peoplewings.libs.bussines import BussinesModel

class notifications_list(BussinesModel):
    sender = models.IntegerField()
    receiver = models.IntegerField()
    created = models.CharField()
    reference = models.CharField()
    read = models.BooleanField()
    title = models.CharField()
    message = models.TextField()
    med_avatar =  models.CharField()
    age = models.IntegerField()
    verified = models.BooleanField()
    location = models.TextField()
    
    _fields_ = ['sender', 'receiver', 'created', 'reference', 'read', 'title', 'message', 'med_avatar', 'age', 'verified', 'location']
