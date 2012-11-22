# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SocialNetwork'
        db.create_table('people_socialnetwork', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('people', ['SocialNetwork'])

        # Adding model 'UserSocialNetwork'
        db.create_table('people_usersocialnetwork', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.UserProfile'])),
            ('social_network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.SocialNetwork'])),
            ('social_network_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('people', ['UserSocialNetwork'])

        # Adding model 'InstantMessage'
        db.create_table('people_instantmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('people', ['InstantMessage'])

        # Adding model 'UserInstantMessage'
        db.create_table('people_userinstantmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.UserProfile'])),
            ('instant_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.InstantMessage'])),
            ('instant_message_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('people', ['UserInstantMessage'])

        # Adding model 'Language'
        db.create_table('people_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('people', ['Language'])

        # Adding model 'UserLanguage'
        db.create_table('people_userlanguage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.UserProfile'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Language'])),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('people', ['UserLanguage'])

        # Adding unique constraint on 'UserLanguage', fields ['user_profile', 'language']
        db.create_unique('people_userlanguage', ['user_profile_id', 'language_id'])

        # Adding model 'University'
        db.create_table('people_university', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('people', ['University'])

        # Adding model 'UserProfileStudiedUniversity'
        db.create_table('people_userprofilestudieduniversity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.UserProfile'])),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.University'])),
            ('degree', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('people', ['UserProfileStudiedUniversity'])

        # Adding model 'Interests'
        db.create_table('people_interests', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(unique=True, max_length=6)),
        ))
        db.send_create_signal('people', ['Interests'])

        # Adding model 'UserProfile'
        db.create_table('people_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('pw_state', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('avatar', self.gf('django.db.models.fields.CharField')(default='http://peoplewings-test-media.s3.amazonaws.com/blank_avatar.jpg', max_length=250)),
            ('medium_avatar', self.gf('django.db.models.fields.CharField')(default='http://peoplewings-test-media.s3.amazonaws.com/med-blank_avatar.jpg', max_length=250, blank=True)),
            ('thumb_avatar', self.gf('django.db.models.fields.CharField')(default='http://peoplewings-test-media.s3.amazonaws.com/thumb-blank_avatar.jpg', max_length=250, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('show_birthday', self.gf('django.db.models.fields.CharField')(default='F', max_length=100)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='Male', max_length=6)),
            ('civil_state', self.gf('django.db.models.fields.CharField')(default='', max_length=2, null=True, blank=True)),
            ('current_city', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cc+', null=True, to=orm['locations.City'])),
            ('hometown', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ht+', null=True, to=orm['locations.City'])),
            ('emails', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('all_about_you', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('main_mission', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('personal_philosophy', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('political_opinion', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('religion', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('enjoy_people', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('movies', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('sports', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('other_pages', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('sharing', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('incredible', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('inspired_by', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('quotes', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('pw_opinion', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('places_lived_in', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('places_visited', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('places_gonna_go', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
            ('places_wanna_go', self.gf('django.db.models.fields.TextField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('people', ['UserProfile'])

        # Adding M2M table for field interested_in on 'UserProfile'
        db.create_table('people_userprofile_interested_in', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['people.userprofile'], null=False)),
            ('interests', models.ForeignKey(orm['people.interests'], null=False))
        ))
        db.create_unique('people_userprofile_interested_in', ['userprofile_id', 'interests_id'])

        # Adding M2M table for field other_locations on 'UserProfile'
        db.create_table('people_userprofile_other_locations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['people.userprofile'], null=False)),
            ('city', models.ForeignKey(orm['locations.city'], null=False))
        ))
        db.create_unique('people_userprofile_other_locations', ['userprofile_id', 'city_id'])

        # Adding model 'Relationship'
        db.create_table('people_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender', to=orm['people.UserProfile'])),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='receiver', to=orm['people.UserProfile'])),
            ('relationship_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('people', ['Relationship'])

        # Adding unique constraint on 'Relationship', fields ['sender', 'receiver']
        db.create_unique('people_relationship', ['sender_id', 'receiver_id'])

        # Adding model 'Reference'
        db.create_table('people_reference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='author', to=orm['people.UserProfile'])),
            ('commented', self.gf('django.db.models.fields.related.ForeignKey')(related_name='commented', to=orm['people.UserProfile'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('punctuation', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('people', ['Reference'])


    def backwards(self, orm):
        # Removing unique constraint on 'Relationship', fields ['sender', 'receiver']
        db.delete_unique('people_relationship', ['sender_id', 'receiver_id'])

        # Removing unique constraint on 'UserLanguage', fields ['user_profile', 'language']
        db.delete_unique('people_userlanguage', ['user_profile_id', 'language_id'])

        # Deleting model 'SocialNetwork'
        db.delete_table('people_socialnetwork')

        # Deleting model 'UserSocialNetwork'
        db.delete_table('people_usersocialnetwork')

        # Deleting model 'InstantMessage'
        db.delete_table('people_instantmessage')

        # Deleting model 'UserInstantMessage'
        db.delete_table('people_userinstantmessage')

        # Deleting model 'Language'
        db.delete_table('people_language')

        # Deleting model 'UserLanguage'
        db.delete_table('people_userlanguage')

        # Deleting model 'University'
        db.delete_table('people_university')

        # Deleting model 'UserProfileStudiedUniversity'
        db.delete_table('people_userprofilestudieduniversity')

        # Deleting model 'Interests'
        db.delete_table('people_interests')

        # Deleting model 'UserProfile'
        db.delete_table('people_userprofile')

        # Removing M2M table for field interested_in on 'UserProfile'
        db.delete_table('people_userprofile_interested_in')

        # Removing M2M table for field other_locations on 'UserProfile'
        db.delete_table('people_userprofile_other_locations')

        # Deleting model 'Relationship'
        db.delete_table('people_relationship')

        # Deleting model 'Reference'
        db.delete_table('people_reference')


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
            'thumb_avatar': ('django.db.models.fields.CharField', [], {'default': "'http://peoplewings-test-media.s3.amazonaws.com/thumb-blank_avatar.jpg'", 'max_length': '250', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['people']