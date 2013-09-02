from django.db import connection, transaction
from peoplewings.apps.people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN last_js bigint NOT NULL default 0")
		cursor.close()
		print 'last_js column added succesfully'


	except Exception, e:
		transaction.rollback()
		print 'last_js column did not get added properly'
		print e
	else:
		transaction.commit()