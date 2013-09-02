from django.db import connection, transaction
from peoplewings.apps.people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN search_score integer NOT NULL default 0")
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN ambassator boolean default false")
		cursor.close()
		print 'ambassator and search_score columns added succesfully'


	except Exception, e:
		transaction.rollback()
		print 'ambassator and search_score columns did not get added properly'
		print e
	else:
		transaction.commit()