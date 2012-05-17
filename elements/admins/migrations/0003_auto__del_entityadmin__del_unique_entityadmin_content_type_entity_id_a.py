# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'EntityAdmin', fields ['content_type', 'entity_id', 'admin']
        db.delete_unique('admins_entityadmin', ['content_type_id', 'entity_id', 'admin_id'])

        # Deleting model 'EntityAdmin'
        db.delete_table('admins_entityadmin')

    def backwards(self, orm):
        # Adding model 'EntityAdmin'
        db.create_table('admins_entityadmin', (
            ('entity_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='administered_entities', to=orm['users.Profile'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('admins', ['EntityAdmin'])

        # Adding unique constraint on 'EntityAdmin', fields ['content_type', 'entity_id', 'admin']
        db.create_unique('admins_entityadmin', ['content_type_id', 'entity_id', 'admin_id'])

    models = {
        
    }

    complete_apps = ['admins']