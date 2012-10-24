# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'City.short_name'
        db.delete_column('locations_city', 'short_name')

        # Deleting field 'Region.short_name'
        db.delete_column('locations_region', 'short_name')

        # Deleting field 'Region.lon'
        db.delete_column('locations_region', 'lon')

        # Deleting field 'Region.lat'
        db.delete_column('locations_region', 'lat')

        # Deleting field 'Country.short_name'
        db.delete_column('locations_country', 'short_name')

        # Deleting field 'Country.lon'
        db.delete_column('locations_country', 'lon')

        # Deleting field 'Country.lat'
        db.delete_column('locations_country', 'lat')


    def backwards(self, orm):
        # Adding field 'City.short_name'
        db.add_column('locations_city', 'short_name',
                      self.gf('django.db.models.fields.CharField')(default='NoName', max_length=200),
                      keep_default=False)

        # Adding field 'Region.short_name'
        db.add_column('locations_region', 'short_name',
                      self.gf('django.db.models.fields.CharField')(default='NoName', max_length=200),
                      keep_default=False)

        # Adding field 'Region.lon'
        db.add_column('locations_region', 'lon',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=12, decimal_places=9),
                      keep_default=False)

        # Adding field 'Region.lat'
        db.add_column('locations_region', 'lat',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=11, decimal_places=9),
                      keep_default=False)

        # Adding field 'Country.short_name'
        db.add_column('locations_country', 'short_name',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=200, unique=True),
                      keep_default=False)

        # Adding field 'Country.lon'
        db.add_column('locations_country', 'lon',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=12, decimal_places=9),
                      keep_default=False)

        # Adding field 'Country.lat'
        db.add_column('locations_country', 'lat',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=11, decimal_places=9),
                      keep_default=False)


    models = {
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
        }
    }

    complete_apps = ['locations']