# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'EntityPost'
        db.delete_table('posts_entitypost')


    def backwards(self, orm):
        # Adding model 'EntityPost'
        db.create_table('posts_entitypost', (
            ('content', self.gf('elements.models.HTMLField')()),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='post_entities', to=orm['users.Profile'])),
            ('entity_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('opinion', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('add_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True, db_index=True)),
        ))
        db.send_create_signal('posts', ['EntityPost'])


    models = {
        
    }

    complete_apps = ['posts']