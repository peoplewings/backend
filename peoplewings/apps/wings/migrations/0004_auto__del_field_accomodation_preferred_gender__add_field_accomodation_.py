# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Accomodation.preferred_gender'
        db.delete_column('wings_accomodation', 'preferred_gender')

        # Adding field 'Accomodation.preferred_male'
        db.add_column('wings_accomodation', 'preferred_male',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Accomodation.preferred_female'
        db.add_column('wings_accomodation', 'preferred_female',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Accomodation.preferred_gender'
        db.add_column('wings_accomodation', 'preferred_gender',
                      self.gf('django.db.models.fields.CharField')(default='B', max_length=1),
                      keep_default=False)

        # Deleting field 'Accomodation.preferred_male'
        db.delete_column('wings_accomodation', 'preferred_male')

        # Deleting field 'Accomodation.preferred_female'
        db.delete_column('wings_accomodation', 'preferred_female')


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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'people.interests': {
            'Meta': {'object_name': 'Interests'},
            'gender': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'people.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
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
            'instant_message_username': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
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
            'company': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
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
            'movies': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'other_locations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'ol+'", 'null': 'True', 'to': "orm['locations.City']"}),
            'other_pages': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'personal_philosophy': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'places_gonna_go': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'places_lived_in': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'places_visited': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'places_wanna_go': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'political_opinion': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'pw_opinion': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'pw_state': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'quotes': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.UserProfile']", 'through': "orm['people.Relationship']", 'symmetrical': 'False'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'sharing': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
            'show_birthday': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '100'}),
            'social_networks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.SocialNetwork']", 'through': "orm['people.UserSocialNetwork']", 'symmetrical': 'False'}),
            'sports': ('django.db.models.fields.TextField', [], {'max_length': '250', 'blank': 'True'}),
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
            'social_network_username': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.UserProfile']"})
        },
        'wings.accomodation': {
            'Meta': {'object_name': 'Accomodation', '_ormbases': ['wings.Wing']},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'additional_information': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'blankets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'capacity': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '1'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.City']", 'on_delete': 'models.PROTECT'}),
            'i_have_pet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'live_center': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'others': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pets_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'preferred_female': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'preferred_male': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sharing_once': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'smoking': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'train': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tram': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'underground': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wheelchair': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'where_sleeping_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'wing_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['wings.Wing']", 'unique': 'True', 'primary_key': 'True'})
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

    complete_apps = ['wings']