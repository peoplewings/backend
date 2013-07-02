from django.db import connection, transaction
from people.models import PhotoAlbums, UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		profs = UserProfile.objects.all()
		for prof in profs:
			try:
				PhotoAlbums.objects.get(author=prof)
			except:
				PhotoAlbums.objects.create(author=prof, name= 'default', ordering=1)
		print 'PhotoAlbums created for every profile'
	except Exception, e:
		transaction.rollback()
		print 'PhotoAlbums did not get created properly'
		print e
	else:
		transaction.commit()