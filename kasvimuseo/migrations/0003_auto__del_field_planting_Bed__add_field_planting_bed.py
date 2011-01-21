# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming field 'Planting.Bed' to 'Planting.bed')
        db.rename_column('kasvimuseo_planting', 'Bed_id', 'bed_id')


    def backwards(self, orm):

        # Renaming field 'Planting.bed' to 'Planting.Bed')
        db.rename_column('kasvimuseo_planting', 'bed_id', 'Bed_id')


    models = {
        'kasvimuseo.bed': {
            'Meta': {'object_name': 'Bed'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Plot']", 'null': 'True', 'blank': 'True'})
        },
        'kasvimuseo.care': {
            'Meta': {'object_name': 'Care'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'planting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Planting']"})
        },
        'kasvimuseo.contact': {
            'Meta': {'object_name': 'Contact'},
            'apartment': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        'kasvimuseo.location': {
            'Meta': {'object_name': 'Location'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'apartment': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kasvimuseo.Contact']", 'through': "orm['kasvimuseo.LocationContact']", 'symmetrical': 'False'}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'village': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        'kasvimuseo.locationcontact': {
            'Meta': {'object_name': 'LocationContact', 'db_table': "'kasvimuseo_location_contacts'"},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Location']"})
        },
        'kasvimuseo.observation': {
            'Meta': {'object_name': 'Observation'},
            'characteristics': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'external_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Location']"}),
            'pictures': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Species']"}),
            'stories': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'kasvimuseo.planting': {
            'Meta': {'object_name': 'Planting'},
            'bed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Bed']"}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Observation']"}),
            'planting_date': ('django.db.models.fields.DateField', [], {}),
            'removal_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'kasvimuseo.plot': {
            'Meta': {'object_name': 'Plot'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'kasvimuseo.species': {
            'Meta': {'object_name': 'Species'},
            'abbr_fi': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'abbr_scientific': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'flower_color': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'flowering_time': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'height': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_fi': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name_local': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'name_sv': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'spacing': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'subspecies': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'substrate': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'variety': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'width': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        }
    }

    complete_apps = ['kasvimuseo']
