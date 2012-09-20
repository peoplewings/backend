from django.db import models
from people.models import UserProfile
from wings.models import Wing

max_text_msg_len = 1000
max_short_text_len = 200
max_ultra_short_len = 10

# Notifications class
class Notification(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='%(app_label)s_%(class)s_receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, related_name='%(app_label)s_%(class)s_sender', on_delete=models.CASCADE)
    timestamp = models.DateField(auto_now_add=True)
    class Meta:
        abstract = True

# Messages class
class Message(Notification): 
    text = models.TextField(blank=True)

# Requests class
class Request(Notification):
    wing1 = models.ForeignKey(Wing, related_name='wing1', on_delete=models.CASCADE)
    wing2 = models.ForeignKey(Wing, related_name='wing2', on_delete=models.CASCADE)
    text1 = models.TextField(max_length=max_text_msg_len, blank=True)
    text2 = models.TextField(max_length=max_text_msg_len, blank=True)
