# -*- coding: utf-8 -*-
import datetime

from django.db.models import F
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Move data from variety field to the new cultivation history field"""
        orm.Species.objects.update(cultivation_history=F(u'variety'),
                                   variety=u'')

    def backwards(self, orm):
        """Move data back from the new cultivation history field

        Data is moved to the variety field. Note that the maximum length for
        the variety field is 40 characters.

        """
        orm.Species.objects.update(variety=F(u'cultivation_history'))

    models = {
        u'kasvimuseo.bed': {
            'Meta': {'object_name': 'Bed'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Plot']", 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'kasvimuseo.care': {
            'Meta': {'ordering': "('date',)", 'object_name': 'Care'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'planting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Planting']"})
        },
        u'kasvimuseo.contact': {
            'Meta': {'ordering': "('last_name',)", 'object_name': 'Contact'},
            'apartment': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        u'kasvimuseo.location': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Location'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'apartment': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['kasvimuseo.Contact']", 'through': u"orm['kasvimuseo.LocationContact']", 'symmetrical': 'False'}),
            'external_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'village': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        u'kasvimuseo.locationcontact': {
            'Meta': {'unique_together': "(('location', 'contact'),)", 'object_name': 'LocationContact', 'db_table': "'kasvimuseo_location_contacts'"},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Location']"})
        },
        u'kasvimuseo.observation': {
            'Meta': {'ordering': "('species__name_fi',)", 'object_name': 'Observation'},
            'characteristics': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'environment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'external_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Location']"}),
            'pictures': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Species']"}),
            'stories': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'variation': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'kasvimuseo.planting': {
            'Meta': {'ordering': "('observation__species__name_fi',)", 'object_name': 'Planting'},
            'bed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Bed']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'depth': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'distance_front': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'distance_left': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Observation']"}),
            'planting_date': ('django.db.models.fields.DateField', [], {}),
            'removal_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '15'})
        },
        u'kasvimuseo.plantingphoto': {
            'Meta': {'object_name': 'PlantingPhoto'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'planting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kasvimuseo.Planting']"})
        },
        u'kasvimuseo.plot': {
            'Meta': {'object_name': 'Plot'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'kasvimuseo.species': {
            'Meta': {'ordering': "('name_fi',)", 'object_name': 'Species'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cultivation_history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'external_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flower_color': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'flowering_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flowering_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'height': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lighting': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name_fi': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['photologue.Photo']", 'null': 'True', 'blank': 'True'}),
            'spacing': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'subspecies': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'substrate': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'variety': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'width': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'photologue.photo': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Photo'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop_from': ('django.db.models.fields.CharField', [], {'default': "'center'", 'max_length': '10', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_related'", 'null': 'True', 'to': u"orm['photologue.PhotoEffect']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('photologue.models.TagField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'photologue.photoeffect': {
            'Meta': {'object_name': 'PhotoEffect'},
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '7'}),
            'brightness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'color': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'contrast': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filters': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'reflection_size': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reflection_strength': ('django.db.models.fields.FloatField', [], {'default': '0.6'}),
            'sharpness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'transpose_method': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        }
    }

    complete_apps = ['kasvimuseo']
    symmetrical = True
