# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Country', fields ['name']
        db.create_unique('locations_country', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Country', fields ['name']
        db.delete_unique('locations_country', ['name'])


    models = {
        'locations.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '9'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Region']"}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "'NoName'", 'max_length': '200'})
        },
        'locations.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '9'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'locations.region': {
            'Meta': {'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '9'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'NoName'", 'max_length': '200'}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "'NoName'", 'max_length': '200'})
        }
    }

    complete_apps = ['locations']