from django.core.management.base import BaseCommand, CommandError
from peoplewings.libs.customauth.models import ApiToken

class Command(BaseCommand):

	def handle(self, *args, **options):
		try:
			ApiToken.cron_delete_inactive_tokens()
		except Exception, e:
			raise CommandError("ERROR while deleting inactive tokens: %s\n" %e)
		self.stdout.write("Inactive tokens deleted succesfully\n")