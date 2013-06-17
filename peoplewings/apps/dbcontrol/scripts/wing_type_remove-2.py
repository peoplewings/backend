from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE wings_wing DROP COLUMN wing_type")
		cursor.close()
		print 'Wing Type Column removed succesfully'
	except Exception, e:
		transaction.rollback()
		print 'Wing Type Column did not get removed properly'
		print e
	else:
		transaction.commit()

