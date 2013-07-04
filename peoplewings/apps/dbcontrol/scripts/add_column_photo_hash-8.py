from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_photos ADD COLUMN photo_hash character varying(50) NOT NULL default ''")
		cursor.close()
		print 'photo hash added succesfully'
	except Exception, e:
		transaction.rollback()
		print 'photo hash did not get added properly'
		print e
	else:
		transaction.commit()