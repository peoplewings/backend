from django.db import connection, transaction
from peoplewings.apps.people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN full_name CHARACTER VARYING(100) NOT NULL default ''")
		cursor.close()
		print 'full name column added succesfully'
		profiles = UserProfile.objects.all()
		for prof in profiles:
			prof.full_name = prof.user.first_name + ' ' + prof.user.last_name
			prof.save()

	except Exception, e:
		transaction.rollback()
		print 'full name column did not get added properly'
		print e
	else:
		transaction.commit()