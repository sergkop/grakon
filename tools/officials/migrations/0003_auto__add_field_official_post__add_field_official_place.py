# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Official.post'
        db.add_column('officials_official', 'post',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Official.place'
        db.add_column('officials_official', 'place',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Official.post'
        db.delete_column('officials_official', 'post')

        # Deleting field 'Official.place'
        db.delete_column('officials_official', 'place')

    models = {
        'officials.official': {
            'Meta': {'object_name': 'Official'},
            'about': ('elements.models.HTMLField', [], {'blank': 'True'}),
            'add_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150'}),
            'post': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['officials']