from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE customauth_apitoken ADD COLUMN remember boolean NOT NULL DEFAULT false")
		cursor.close()
	except Exception, e:
		transaction.rollback()
		print 'Remember-Apitoken did not get executed properly'
		print e
	else:
		transaction.commit()

