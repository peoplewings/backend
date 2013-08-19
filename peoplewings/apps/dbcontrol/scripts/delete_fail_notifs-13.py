from django.db import connection, transaction
from django.db.models import Q
from peoplewings.apps.notifications.models import Notifications, Requests, Invites, AdditionalInformation, AccomodationInformation, NotificationsAlarm

@transaction.commit_manually
def main():
	#We have to create a new DB column in the apiToken model called remember
	try:
		notifications = Notifications.objects.filter(~Q(kind='message'))
		for notifs in notifications:
			if not AccomodationInformation.objects.filter(notification__pk=notifs.pk).count():
				#delete the notification along the notification alarm
				alarms = NotificationsAlarm.objects.filter(reference=notifs.reference)
				for ala in alarms:
					ala.delete()
				notifs.delete()
		print 'failed notifs removed succesfully'

		alarms = NotificationsAlarm.objects.all()
		for ala in alarms:
			if not Notifications.objects.filter(reference=ala.reference).count():
				ala.delete()

	except Exception, e:
		transaction.rollback()
		print 'failed notifs did not get removed properly'
		print e
	else:
		transaction.commit()