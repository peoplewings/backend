from django.core.management.base import BaseCommand, CommandError
from registration.models import RegistrationProfile

class Command(BaseCommand):

	def handle(self, *args, **options):
		try:
			RegistrationProfile.cron_delete_inactive_accounts()
		except Exception, e:
			raise CommandError("ERROR while deleting inactive users: %s\n" %e)
		self.stdout.write("Inactive users deleted succesfully\n")