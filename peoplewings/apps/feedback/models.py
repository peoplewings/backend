from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import User

FTYPE_CHOICES = (
        ('Problem', 'Problem'),
        ('Advice', 'Advice'),
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
    )

class Feedback(models.Model):

    class Meta:
        verbose_name = "Feedbacks"
        verbose_name_plural = "Feedback"        
 
    text = models.TextField(max_length=500, null=False, blank=False)
    ftype = models.CharField(max_length=10, choices=FTYPE_CHOICES, null=False)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, unique=False)
    browser = models.CharField(max_length=80, null=True, blank=True)

