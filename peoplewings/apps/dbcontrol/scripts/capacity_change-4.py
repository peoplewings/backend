from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE wings_accomodation ALTER COLUMN capacity TYPE character varying(2)")
		cursor.close()
		print 'Capacity Column of accomodation changed succesfully'
	except Exception, e:
		transaction.rollback()
		print 'Capacity Column of accomodation did not get changed properly'
		print e
	else:
		transaction.commit()

