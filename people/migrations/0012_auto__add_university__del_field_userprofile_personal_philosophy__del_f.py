# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'University'
        db.create_table('people_university', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('people', ['University'])

        # Deleting field 'UserProfile.personal_philosophy'
        db.delete_column('people_userprofile', 'personal_philosophy')

        # Deleting field 'UserProfile.what_you_like_sharing'
        db.delete_column('people_userprofile', 'what_you_like_sharing')

        # Deleting field 'UserProfile.pw_experience'
        db.delete_column('people_userprofile', 'pw_experience')

        # Deleting field 'UserProfile.quotes'
        db.delete_column('people_userprofile', 'quotes')

        # Deleting field 'UserProfile.pw_opinion'
        db.delete_column('people_userprofile', 'pw_opinion')

        # Deleting field 'UserProfile.people_inspired_you'
        db.delete_column('people_userprofile', 'people_inspired_you')

        # Deleting field 'UserProfile.education'
        db.delete_column('people_userprofile', 'education')

        # Deleting field 'UserProfile.occupation'
        db.delete_column('people_userprofile', 'occupation')

        # Deleting field 'UserProfile.people_you_like'
        db.delete_column('people_userprofile', 'people_you_like')

        # Deleting field 'UserProfile.religion'
        db.delete_column('people_userprofile', 'religion')

        # Deleting field 'UserProfile.incredible_done_seen'
        db.delete_column('people_userprofile', 'incredible_done_seen')

        # Deleting field 'UserProfile.political_opinion'
        db.delete_column('people_userprofile', 'political_opinion')

        # Deleting field 'UserProfile.favourite_movies_series_others'
        db.delete_column('people_userprofile', 'favourite_movies_series_others')

        # Deleting field 'UserProfile.main_mission'
        db.delete_column('people_userprofile', 'main_mission')

        # Deleting field 'UserProfile.other_pages_you_like'
        db.delete_column('people_userprofile', 'other_pages_you_like')

        # Adding field 'UserProfile.universities'
        db.add_column('people_userprofile', 'universities',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'University'
        db.delete_table('people_university')

        # Adding field 'UserProfile.personal_philosophy'
        db.add_column('people_userprofile', 'personal_philosophy',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.what_you_like_sharing'
        db.add_column('people_userprofile', 'what_you_like_sharing',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.pw_experience'
        db.add_column('people_userprofile', 'pw_experience',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.quotes'
        db.add_column('people_userprofile', 'quotes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.pw_opinion'
        db.add_column('people_userprofile', 'pw_opinion',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.people_inspired_you'
        db.add_column('people_userprofile', 'people_inspired_you',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.education'
        db.add_column('people_userprofile', 'education',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.occupation'
        db.add_column('people_userprofile', 'occupation',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.people_you_like'
        db.add_column('people_userprofile', 'people_you_like',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.religion'
        db.add_column('people_userprofile', 'religion',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.incredible_done_seen'
        db.add_column('people_userprofile', 'incredible_done_seen',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.political_opinion'
        db.add_column('people_userprofile', 'political_opinion',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.favourite_movies_series_others'
        db.add_column('people_userprofile', 'favourite_movies_series_others',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.main_mission'
        db.add_column('people_userprofile', 'main_mission',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.other_pages_you_like'
        db.add_column('people_userprofile', 'other_pages_you_like',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Deleting field 'UserProfile.universities'
        db.delete_column('people_userprofile', 'universities')


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
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
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
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interested_in': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Languages']", 'symmetrical': 'False'}),
            'pw_state': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.UserProfile']", 'through': "orm['people.Relationship']", 'symmetrical': 'False'}),
            'universities': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['people']