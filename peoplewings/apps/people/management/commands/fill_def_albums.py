from django.core.management.base import BaseCommand, CommandError
from people.models import UserProfile, PhotoAlbums

class Command(BaseCommand):

	def handle(self, *args, **options):
		try:
			profs = UserProfile.objects.all()
			for prof in profs:
				import pdb; pdb.set_trace()
				try:
					if len(PhotoAlbums.objects.filter(author=prof)) == 0:
						alb = PhotoAlbums.objects.create(name='default',author=prof)
				except:
					pass
		except Exception, e:
			raise CommandError("ERROR while updating reply rate and time: %s\n" %e)
		self.stdout.write("Albums updated succesfully\n")