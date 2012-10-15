import datetime
import hmac
import time
from django.conf import settings
from django.db import models

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

if 'django.contrib.auth' in settings.INSTALLED_APPS:
    import uuid
    from django.conf import settings
    from django.contrib.auth.models import User

class ApiToken(models.Model):
    user = models.ForeignKey(User, related_name='api_tokens')
    token = models.CharField(max_length=256, blank=True, default='')
    last = models.DateTimeField()

    def __unicode__(self):
        return u"Token %s for %s used at %s" % (
            self.token, self.user, self.last)

    def generate_token(self):
        # Concatenate two uuids.
        uuids = [uuid.uuid4() for i in range(2)]

        # Get the hmac.
        hmacs = [hmac.new(str(u), digestmod=sha1) for u in uuids]

        # Return the concatenation.
        return ''.join([h.hexdigest() for h in hmacs])

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super(ApiToken, self).save(*args, **kwargs)

    #def get_or_create(self, *args, **kwargs):
        
    def is_valid(self, now=datetime.datetime.now()):
        " Check if token is still valid."

        # Get valid period.
        valid_time = getattr(settings, 'TOKEN_VALID_TIME', 3600)

        if (now - self.last) < datetime.timedelta(seconds=valid_time):
            self.last = now
            self.save()
            return True
        return False

