from django.core.management.base import BaseCommand, CommandError
from people.models import UserProfile

class Command(BaseCommand):

	def handle(self, *args, **options):
		try:
			UserProfile.cron_reply_rate()
		except Exception, e:
			raise CommandError("ERROR while updating reply rate and time: %s\n" %e)
		self.stdout.write("Reply rate and reply time updated succesfully\n")