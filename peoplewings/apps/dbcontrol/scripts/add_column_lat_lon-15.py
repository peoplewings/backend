from django.db import connection, transaction
from peoplewings.apps.people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN last_login_lat numeric(11,9) NOT NULL default 0.0")
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN last_login_lon numeric(11,9) NOT NULL default 0.0")
		cursor.close()
		print 'lat lon column added succesfully'


	except Exception, e:
		transaction.rollback()
		print 'lat lon column did not get added properly'
		print e
	else:
		transaction.commit()