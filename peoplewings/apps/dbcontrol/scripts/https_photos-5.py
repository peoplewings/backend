from django.db import connection, transaction
from people.models import UserProfile

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		profs = UserProfile.objects.al()
		for prof in profs:
			prof.avatar = str.replace(prof.avatar, 'http', '', 1)
			prof.medium_avatar = str.replace(prof.medium_avatar, 'http', '', 1)
			prof.thumb_avatar = str.replace(prof.thumb_avatar, 'http', '', 1)
			prof.blur_avatar = str.replace(prof.blur_avatar, 'http', '', 1)
			prof.save()
		transaction.commit()

