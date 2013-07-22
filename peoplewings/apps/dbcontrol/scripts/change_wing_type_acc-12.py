from django.db import connection, transaction
from peoplewings.apps.wings.models import Wing

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		wings = Wing.objects.filter(wing_type = 'Accomodation')
		for w in wings:
			w.wing_type = 'Accommodation'
			w.save()
		print 'wing type column changed succesfully'
	except Exception, e:
		transaction.rollback()
		print 'wing type column did not get changed added properly'
		print e
	else:
		transaction.commit()