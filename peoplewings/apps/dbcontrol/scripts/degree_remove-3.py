from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE people_userprofilestudieduniversity DROP COLUMN degree")
		cursor.close()
		print 'Degree Column of profileUniversity removed succesfully'
	except Exception, e:
		transaction.rollback()
		print 'Degree Column of profileUniversity did not get removed properly'
		print e
	else:
		transaction.commit()

