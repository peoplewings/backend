# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Notifications'
        db.create_table('notifications_notifications', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications_receiver', to=orm['people.UserProfile'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications_sender', to=orm['people.UserProfile'])),
            ('created', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=15, null=True)),
            ('first_sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications_first_sender', null=True, to=orm['people.UserProfile'])),
        ))
        db.send_create_signal('notifications', ['Notifications'])

        # Adding model 'Requests'
        db.create_table('notifications_requests', (
            ('notifications_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['notifications.Notifications'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('public_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('private_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('make_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requests_wing', to=orm['wings.Wing'])),
        ))
        db.send_create_signal('notifications', ['Requests'])

        # Adding model 'Invites'
        db.create_table('notifications_invites', (
            ('notifications_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['notifications.Notifications'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('private_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('wing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invites_wing', to=orm['wings.Wing'])),
        ))
        db.send_create_signal('notifications', ['Invites'])

        # Adding model 'Messages'
        db.create_table('notifications_messages', (
            ('notifications_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['notifications.Notifications'], unique=True, primary_key=True)),
            ('private_message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('notifications', ['Messages'])

        # Adding model 'Friendship'
        db.create_table('notifications_friendship', (
            ('notifications_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['notifications.Notifications'], unique=True, primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('notifications', ['Friendship'])

        # Adding model 'AccomodationInformation'
        db.create_table('notifications_accomodationinformation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='accomodationinformation_notification', to=orm['notifications.Notifications'])),
            ('modified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start_date', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('end_date', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('transport', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('num_people', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('notifications', ['AccomodationInformation'])

        # Adding model 'NotificationsAlarm'
        db.create_table('notifications_notificationsalarm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alarm_receiver', to=orm['people.UserProfile'])),
            ('notificated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('notifications', ['NotificationsAlarm'])


    def backwards(self, orm):
        # Deleting model 'Notifications'
        db.delete_table('notifications_notifications')

        # Deleting model 'Requests'
        db.delete_table('notifications_requests')

        # Deleting model 'Invites'
        db.delete_table('notifications_invites')

        # Deleting model 'Messages'
        db.delete_table('notifications_messages')

        # Deleting model 'Friendship'
        db.delete_table('notifications_friendship')

        # Deleting model 'AccomodationInformation'
        db.delete_table('notifications_accomodationinformation')

        # Deleting model 'NotificationsAlarm'
        db.delete_table('notifications_notificationsalarm')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'locations.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '9'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Region']"})
        },
        'locations.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'locations.region': {
            'Meta': {'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'NoName'", 'max_length': '200'})
        },
        'notifications.accomodationinformation': {
            'Meta': {'object_name': 'AccomodationInformation'},
            'end_date': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accomodationinformation_notification'", 'to': "orm['notifications.Notifications']"}),
            'num_people': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'start_date': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'transport': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'notifications.friendship': {
            'Meta': {'object_name': 'Friendship', '_ormbases': ['notifications.Notifications']},
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notifications_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['notifications.Notifications']", 'unique': 'True', 'primary_key': 'True'})
        },
        'notifications.invites': {
            'Meta': {'object_name': 'Invites', '_ormbases': ['notifications.Notifications']},
            'notifications_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['notifications.Notifications']", 'unique': 'True', 'primary_key': 'True'}),
            'private_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'wing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites_wing'", 'to': "orm['wings.Wing']"})
        },
        'notifications.messages': {
            'Meta': {'object_name': 'Messages', '_ormbases': ['notifications.Notifications']},
            'notifications_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['notifications.Notifications']", 'unique': 'True', 'primary_key': 'True'}),
            'private_message': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'notifications.notifications': {
            'Meta': {'object_name': 'Notifications'},
            'created': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'first_sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications_first_sender'", 'null': 'True', 'to': "orm['people.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications_receiver'", 'to': "orm['people.UserProfile']"}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications_sender'", 'to': "orm['people.UserProfile']"})
        },
        'notifications.notificationsalarm': {
            'Meta': {'object_name': 'NotificationsAlarm'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notificated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alarm_receiver'", 'to': "orm['people.UserProfile']"}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'notifications.requests': {
            'Meta': {'object_name': 'Requests', '_ormbases': ['notifications.Notifications']},
            'make_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notifications_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['notifications.Notifications']", 'unique': 'True', 'primary_key': 'True'}),
            'private_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'public_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'wing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requests_wing'", 'to': "orm['wings.Wing']"})
        },
        'people.instantmessage': {
            'Meta': {'object_name': 'InstantMessage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'people.interests': {
            'Meta': {'object_name': 'Interests'},
            'gender': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'people.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'people.reference': {
            'Meta': {'object_name': 'Reference'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'author'", 'to': "orm['people.UserProfile']"}),
            'commented': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commented'", 'to': "orm['people.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'punctuation': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'people.relationship': {
            'Meta': {'unique_together': "(('sender', 'receiver'),)", 'object_name': 'Relationship'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receiver'", 'to': "orm['people.UserProfile']"}),
            'relationship_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'to': "orm['people.UserProfile']"})
        },
        'people.socialnetwork': {
            'Meta': {'object_name': 'SocialNetwork'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'people.university': {
            'Meta': {'object_name': 'University'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'people.userinstantmessage': {
            'Meta': {'object_name': 'UserInstantMessage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instant_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstantMessage']"}),
            'instant_message_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.UserProfile']"})
        },
        'people.userlanguage': {
            'Meta': {'unique_together': "(('user_profile', 'language'),)", 'object_name': 'UserLanguage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Language']"}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.UserProfile']"})
        },
        'people.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'age': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'all_about_you': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.CharField', [], {'default': "'http://peoplewings-test-media.s3.amazonaws.com/blank_avatar.jpg'", 'max_length': '250'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'blur_avatar': ('django.db.models.fields.CharField', [], {'default': "'http://peoplewings-test-media.s3.amazonaws.com/med-blank_avatar.jpg'", 'max_length': '250', 'blank': 'True'}),
            'civil_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'current_city': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cc+'", 'null': 'True', 'to': "orm['locations.City']"}),
            'emails': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'enjoy_people': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'Male'", 'max_length': '6'}),
            'hometown': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ht+'", 'null': 'True', 'to': "orm['locations.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incredible': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'inspired_by': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'instant_messages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.InstantMessage']", 'through': "orm['people.UserInstantMessage']", 'symmetrical': 'False'}),
            'interested_in': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': "orm['people.Interests']", 'null': 'True', 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Language']", 'null': 'True', 'through': "orm['people.UserLanguage']", 'symmetrical': 'False'}),
            'last_login': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ll+'", 'null': 'True', 'to': "orm['locations.City']"}),
            'main_mission': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'medium_avatar': ('django.db.models.fields.CharField', [], {'default': "'http://peoplewings-test-media.s3.amazonaws.com/med-blank_avatar.jpg'", 'max_length': '250', 'blank': 'True'}),
            'movies': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'other_locations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'ol+'", 'null': 'True', 'to': "orm['locations.City']"}),
            'other_pages': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'personal_philosophy': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'places_gonna_go': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'places_lived_in': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'places_visited': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'places_wanna_go': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'political_opinion': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'pw_opinion': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'pw_state': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'quotes': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references+'", 'symmetrical': 'False', 'through': "orm['people.Reference']", 'to': "orm['people.UserProfile']"}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.UserProfile']", 'through': "orm['people.Relationship']", 'symmetrical': 'False'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'sharing': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'show_birthday': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '100'}),
            'social_networks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.SocialNetwork']", 'through': "orm['people.UserSocialNetwork']", 'symmetrical': 'False'}),
            'sports': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'thumb_avatar': ('django.db.models.fields.CharField', [], {'default': "'http://peoplewings-test-media.s3.amazonaws.com/med-blank_avatar.jpg'", 'max_length': '250', 'blank': 'True'}),
            'universities': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.University']", 'through': "orm['people.UserProfileStudiedUniversity']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'people.userprofilestudieduniversity': {
            'Meta': {'object_name': 'UserProfileStudiedUniversity'},
            'degree': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.University']"}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.UserProfile']"})
        },
        'people.usersocialnetwork': {
            'Meta': {'object_name': 'UserSocialNetwork'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'social_network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.SocialNetwork']"}),
            'social_network_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.UserProfile']"})
        },
        'wings.wing': {
            'Meta': {'object_name': 'Wing'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.UserProfile']"}),
            'best_days': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Wing'", 'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Y'", 'max_length': '1'})
        }
    }

    complete_apps = ['notifications']