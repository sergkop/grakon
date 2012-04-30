# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Official'
        db.create_table('officials_official', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, db_index=True, blank=True)),
            ('add_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, db_index=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('about', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('officials', ['Official'])

    def backwards(self, orm):
        # Deleting model 'Official'
        db.delete_table('officials_official')

    models = {
        'officials.official': {
            'Meta': {'object_name': 'Official'},
            'about': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
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