from django.db import models

# Create your models here.

class DbControl(models.Model):
	script_path = models.TextField(null=True, blank=True, default='')
	applied = models.BooleanField(null=False, default=False)
