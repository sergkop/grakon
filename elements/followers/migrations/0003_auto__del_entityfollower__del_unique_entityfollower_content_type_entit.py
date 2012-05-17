# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'EntityFollower', fields ['content_type', 'entity_id', 'follower']
        db.delete_unique('followers_entityfollower', ['content_type_id', 'entity_id', 'follower_id'])

        # Deleting model 'EntityFollower'
        db.delete_table('followers_entityfollower')

    def backwards(self, orm):
        # Adding model 'EntityFollower'
        db.create_table('followers_entityfollower', (
            ('entity_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('follower', self.gf('django.db.models.fields.related.ForeignKey')(related_name='followed_entities', to=orm['users.Profile'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('followers', ['EntityFollower'])

        # Adding unique constraint on 'EntityFollower', fields ['content_type', 'entity_id', 'follower']
        db.create_unique('followers_entityfollower', ['content_type_id', 'entity_id', 'follower_id'])

    models = {
        
    }

    complete_apps = ['followers']