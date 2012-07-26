# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserProfile.personal_philosophy'
        db.alter_column('people_userprofile', 'personal_philosophy', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.what_you_like_sharing'
        db.alter_column('people_userprofile', 'what_you_like_sharing', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.pw_experience'
        db.alter_column('people_userprofile', 'pw_experience', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.quotes'
        db.alter_column('people_userprofile', 'quotes', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.pw_opinion'
        db.alter_column('people_userprofile', 'pw_opinion', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.people_inspired_you'
        db.alter_column('people_userprofile', 'people_inspired_you', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.education'
        db.alter_column('people_userprofile', 'education', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'UserProfile.occupation'
        db.alter_column('people_userprofile', 'occupation', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'UserProfile.all_about_you'
        db.alter_column('people_userprofile', 'all_about_you', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.people_you_like'
        db.alter_column('people_userprofile', 'people_you_like', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.religion'
        db.alter_column('people_userprofile', 'religion', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'UserProfile.incredible_done_seen'
        db.alter_column('people_userprofile', 'incredible_done_seen', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.political_opinion'
        db.alter_column('people_userprofile', 'political_opinion', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'UserProfile.favourite_movies_series_others'
        db.alter_column('people_userprofile', 'favourite_movies_series_others', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.main_mission'
        db.alter_column('people_userprofile', 'main_mission', self.gf('django.db.models.fields.TextField')())

        # Changing field 'UserProfile.other_pages_you_like'
        db.alter_column('people_userprofile', 'other_pages_you_like', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'UserProfile.personal_philosophy'
        db.alter_column('people_userprofile', 'personal_philosophy', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.what_you_like_sharing'
        db.alter_column('people_userprofile', 'what_you_like_sharing', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.pw_experience'
        db.alter_column('people_userprofile', 'pw_experience', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.quotes'
        db.alter_column('people_userprofile', 'quotes', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.pw_opinion'
        db.alter_column('people_userprofile', 'pw_opinion', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.people_inspired_you'
        db.alter_column('people_userprofile', 'people_inspired_you', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.education'
        db.alter_column('people_userprofile', 'education', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'UserProfile.occupation'
        db.alter_column('people_userprofile', 'occupation', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'UserProfile.all_about_you'
        db.alter_column('people_userprofile', 'all_about_you', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.people_you_like'
        db.alter_column('people_userprofile', 'people_you_like', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.religion'
        db.alter_column('people_userprofile', 'religion', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'UserProfile.incredible_done_seen'
        db.alter_column('people_userprofile', 'incredible_done_seen', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.political_opinion'
        db.alter_column('people_userprofile', 'political_opinion', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'UserProfile.favourite_movies_series_others'
        db.alter_column('people_userprofile', 'favourite_movies_series_others', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.main_mission'
        db.alter_column('people_userprofile', 'main_mission', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.other_pages_you_like'
        db.alter_column('people_userprofile', 'other_pages_you_like', self.gf('django.db.models.fields.TextField')(null=True))

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
        'people.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'user1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'r1'", 'to': "orm['people.UserProfile']"}),
            'user2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'r2'", 'to': "orm['people.UserProfile']"})
        },
        'people.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'age': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'all_about_you': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'civil_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'favourite_movies_series_others': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incredible_done_seen': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'interested_in': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'main_mission': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'occupation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'other_pages_you_like': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'people_inspired_you': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'people_you_like': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'personal_philosophy': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'political_opinion': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'pw_experience': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'pw_opinion': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'pw_state': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'quotes': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.UserProfile']", 'through': "orm['people.Relationship']", 'symmetrical': 'False'}),
            'religion': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'what_you_like_sharing': ('django.db.models.fields.TextField', [], {'default': "''"})
        }
    }

    complete_apps = ['people']