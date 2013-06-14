from django.core.management.base import BaseCommand, CommandError
from dbcontrol.views import apply_changes, list_changes, one_change
from optparse import make_option

class Command(BaseCommand):

	help= 'Applies certan or all DB scripts in order'
	option_list = BaseCommand.option_list + (
        make_option('--list',
            action='store_true',
            dest='list',
            default=False,
            help='List all available scripts and see if we have applied them'),
        ) + (
        make_option('--one',
            action='store_true',
            dest='one',
            default=False,
            help='Applies the script taged with a certain number'),
        )

	def handle(self, *args, **options):
		if options['list']:
			list_changes()
		elif options['one']:
			for arg in args:
				one_change(arg)
		else:
			apply_changes()
		self.stdout.write("Changes to the DB applyed succesfully\n")