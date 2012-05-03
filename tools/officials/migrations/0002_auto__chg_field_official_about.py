# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Official.about'
        db.alter_column('officials_official', 'about', self.gf('elements.models.HTMLField')())
    def backwards(self, orm):

        # Changing field 'Official.about'
        db.alter_column('officials_official', 'about', self.gf('tinymce.models.HTMLField')())
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
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['officials']