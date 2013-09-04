from django.db import connection, transaction
from peoplewings.apps.people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofile ADD COLUMN landscape_photo character varying(250) NOT NULL default 'http://peoplewings-test-media.s3.amazonaws.com/landscape-default.jpg'::character varying")
		cursor.close()
		print 'landscape column added succesfully'


	except Exception, e:
		transaction.rollback()
		print 'landscape column did not get added properly'
		print e
	else:
		transaction.commit()