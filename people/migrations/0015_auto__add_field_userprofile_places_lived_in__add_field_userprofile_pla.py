# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserProfile.places_lived_in'
        db.add_column('people_userprofile', 'places_lived_in',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.places_wanna_go'
        db.add_column('people_userprofile', 'places_wanna_go',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.places_gonna_go'
        db.add_column('people_userprofile', 'places_gonna_go',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserProfile.places_lived_in'
        db.delete_column('people_userprofile', 'places_lived_in')

        # Deleting field 'UserProfile.places_wanna_go'
        db.delete_column('people_userprofile', 'places_wanna_go')

        # Deleting field 'UserProfile.places_gonna_go'
        db.delete_column('people_userprofile', 'places_gonna_go')


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
        'people.languages': {
            'Meta': {'object_name': 'Languages'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'people.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relationship_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'user1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'r1'", 'to': "orm['people.UserProfile']"}),
            'user2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'r2'", 'to': "orm['people.UserProfile']"})
        },
        'people.university': {
            'Meta': {'object_name': 'University'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'people.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'age': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'all_about_you': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'civil_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'favourite_movies_series_others': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incredible_done_seen': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'interested_in': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Languages']", 'symmetrical': 'False'}),
            'main_mission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'other_pages_you_like': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'people_inspired_you': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'people_you_like': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'personal_philosophy': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'places_gonna_go': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'places_lived_in': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'places_wanna_go': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'political_opinion': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'pw_experience': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pw_opinion': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pw_state': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'quotes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.UserProfile']", 'through': "orm['people.Relationship']", 'symmetrical': 'False'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'universities': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.University']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'what_you_like_sharing': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['people']