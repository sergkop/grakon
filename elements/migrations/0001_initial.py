# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EntityResource'
        db.create_table('elements_entityresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('entity_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('resource', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('elements', ['EntityResource'])

        # Adding unique constraint on 'EntityResource', fields ['content_type', 'entity_id', 'resource']
        db.create_unique('elements_entityresource', ['content_type_id', 'entity_id', 'resource'])

        # Adding model 'EntityLocation'
        db.create_table('elements_entitylocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('entity_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entities', to=orm['locations.Location'])),
        ))
        db.send_create_signal('elements', ['EntityLocation'])

        # Adding unique constraint on 'EntityLocation', fields ['content_type', 'entity_id', 'location']
        db.create_unique('elements_entitylocation', ['content_type_id', 'entity_id', 'location_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'EntityLocation', fields ['content_type', 'entity_id', 'location']
        db.delete_unique('elements_entitylocation', ['content_type_id', 'entity_id', 'location_id'])

        # Removing unique constraint on 'EntityResource', fields ['content_type', 'entity_id', 'resource']
        db.delete_unique('elements_entityresource', ['content_type_id', 'entity_id', 'resource'])

        # Deleting model 'EntityResource'
        db.delete_table('elements_entityresource')

        # Deleting model 'EntityLocation'
        db.delete_table('elements_entitylocation')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'elements.entitylocation': {
            'Meta': {'unique_together': "(('content_type', 'entity_id', 'location'),)", 'object_name': 'EntityLocation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entities'", 'to': "orm['locations.Location']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'elements.entityresource': {
            'Meta': {'unique_together': "(('content_type', 'entity_id', 'resource'),)", 'object_name': 'EntityResource'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'locations.location': {
            'Meta': {'object_name': 'Location'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'country_related'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'district_related'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'okato_id': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'region_related'", 'null': 'True', 'to': "orm['locations.Location']"})
        }
    }

    complete_apps = ['elements']