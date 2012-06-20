# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Official'
        db.delete_table('officials_official')


    def backwards(self, orm):
        # Adding model 'Official'
        db.create_table('officials_official', (
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('post', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('add_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True, db_index=True)),
            ('about', self.gf('elements.models.HTMLField')(blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('place', self.gf('django.db.models.fields.CharField')(default='', max_length=150)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True, db_index=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('officials', ['Official'])


    models = {
        
    }

    complete_apps = ['officials']