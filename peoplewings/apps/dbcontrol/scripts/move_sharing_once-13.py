from django.db import connection, transaction

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		#Create column sharing_once in wing model
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE wings_wing ADD COLUMN sharing_once2 boolean NOT NULL default false")
		cursor.close()
		#Copy data from accommodation to wing
		cursor = connection.cursor()
		cursor.execute('create or replace function mv_sharing() returns void as $$ declare l_wings record; begin for l_wings in select * from wings_accomodation where sharing_once is true loop update wings_wing set sharing_once2 = true where id = l_wings.wing_ptr_id; end loop; end; $$ language "plpgsql" volatile;');
		cursor.execute('select * from mv_sharing()')
		cursor.close()
		#Remove sharing once column from accomodation
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE wings_accomodation DROP COLUMN sharing_once")
		cursor.close()
		cursor = connection.cursor()
		cursor.execute("ALTER TABLE wings_wing RENAME COLUMN sharing_once2 TO sharing_once")
		cursor.close()
		print 'sharing once column changed succesfully'
	except Exception, e:
		transaction.rollback()
		print 'sharing once column did not get changed added properly'
		print e
	else:
		transaction.commit()