from django.core.management.base import BaseCommand, CommandError
from notifications.models import Notifications

class Command(BaseCommand):

	def handle(self, *args, **options):
		try:
			Notifications.objects.cron_send_notif_emails()
		except Exception, e:
			raise CommandError("ERROR while updating email notifs: %s\n" %e)
		self.stdout.write("Email notifs updated succesfully\n")