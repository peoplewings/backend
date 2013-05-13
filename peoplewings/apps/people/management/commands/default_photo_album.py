from django.core.management.base import BaseCommand, CommandError
from peoplewings.apps.people.models import PhotoAlbums, Photos, UserProfile

class Command(BaseCommand):

	def handle(self, *args, **options):
		try:
			profs = UserProfile.objects.all()
			for prof in profs:
				if len(prof.photoalbums_author.all()) == 0:
					PhotoAlbums.objects.create(author=prof, name='default')
		except Exception, e:
			print 'ERROR %s', str(e)