from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE wings_wing ADD COLUMN wing_type CHARACTER VARYING(100) NOT NULL default 'Accomodation'")
		cursor.close()
		print 'wing type column added succesfully'
	except Exception, e:
		transaction.rollback()
		print 'wing type column did not get added properly'
		print e
	else:
		transaction.commit()