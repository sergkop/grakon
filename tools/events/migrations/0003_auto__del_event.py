# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Event'
        db.delete_table('events_event')


    def backwards(self, orm):
        # Adding model 'Event'
        db.create_table('events_event', (
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('place', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('description', self.gf('elements.models.HTMLField')(blank=True)),
            ('event_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('add_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True, db_index=True)),
        ))
        db.send_create_signal('events', ['Event'])


    models = {
        
    }

    complete_apps = ['events']