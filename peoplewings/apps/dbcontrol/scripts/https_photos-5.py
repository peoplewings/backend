from django.db import connection, transaction
from people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		profs = UserProfile.objects.all()
		for prof in profs:
			prof.avatar = str.replace(str(prof.avatar), 'http://', '//', 1)
			prof.medium_avatar = str.replace(str(prof.medium_avatar), 'http://', '//', 1)
			prof.thumb_avatar = str.replace(str(prof.thumb_avatar), 'http://', '//', 1)
			prof.blur_avatar = str.replace(str(prof.blur_avatar), 'http://', '//', 1)
			prof.save()
		print 'Https in photos applyed'
	except Exception, e:
		transaction.rollback()
		print 'Https in photos did not get changed properly'
		print e
	else:
		transaction.commit()

