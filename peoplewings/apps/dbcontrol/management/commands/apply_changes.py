from django.core.management.base import BaseCommand, CommandError
from dbcontrol.views import apply_changes
class Command(BaseCommand):

	def handle(self, *args, **options):
		apply_changes()
		self.stdout.write("Changes to the DB applyed succesfully\n")