from django.db import connection, transaction
from peoplewings.apps.people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN tutorial boolean NOT NULL default false")
		cursor.close()
		print 'tutorial column added succesfully'
	except Exception, e:
		transaction.rollback()
		print 'tutorial column did not get added properly'
		print e
	else:
		transaction.commit()