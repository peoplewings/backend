from django.db import connection, transaction
from people.models import UserProfile
from django.contrib.auth.models import User

from django.utils.hashcompat import sha_constructor
import datetime
import random

@transaction.commit_manually
def main():
	try:
		user = User.objects.create(username='PPW-Team', first_name='The PEOPLEWINGS', last_name='Team', email='accounts-noreply@peoplewings.com', password=sha_constructor(str(random.random())).hexdigest()[:128], is_staff=False, is_active=False, is_superuser=False, last_login=datetime.datetime.now(), date_joined=datetime.datetime.now())
		profile = UserProfile.objects.create(pk=user.pk, user=user, avatar='https://s3-eu-west-1.amazonaws.com/peoplewings-test-media/PEOPLEWINGS4.jpg', medium_avatar='https://s3-eu-west-1.amazonaws.com/peoplewings-test-media/PEOPLEWINGS4.jpg', thumb_avatar='https://s3-eu-west-1.amazonaws.com/peoplewings-test-media/PEOPLEWINGS4.jpg', active=True, gender='Female', birthday=datetime.date(1920, 01, 01))
		print 'SuperUser PPW was created'
	except Exception, e:
		transaction.rollback()
		print 'SuperUser PPW did not create suscesfully'
		print e
	else:
		transaction.commit()