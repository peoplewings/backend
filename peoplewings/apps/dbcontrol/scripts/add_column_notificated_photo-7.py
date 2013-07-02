from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_photos ADD COLUMN add_notificated boolean NOT NULL default false")
		cursor.close()
		print 'add_notificated column of photos added succesfully'
	except Exception, e:
		transaction.rollback()
		print 'add_notificated column of photos did not get added properly'
		print e
	else:
		transaction.commit()

