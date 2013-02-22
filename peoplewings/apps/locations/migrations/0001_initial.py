# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table('locations_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('locations', ['Country'])

        # Adding model 'Region'
        db.create_table('locations_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='NoName', max_length=200)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Country'])),
        ))
        db.send_create_signal('locations', ['Region'])

        # Adding model 'City'
        db.create_table('locations_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lat', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=11, decimal_places=9)),
            ('lon', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=12, decimal_places=9)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Region'])),
        ))
        db.send_create_signal('locations', ['City'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table('locations_country')

        # Deleting model 'Region'
        db.delete_table('locations_region')

        # Deleting model 'City'
        db.delete_table('locations_city')


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