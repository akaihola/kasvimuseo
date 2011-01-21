# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Species'
        db.create_table('kasvimuseo_species', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('external_id', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('genus', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('species', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('subspecies', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('variety', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('name_fi', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('name_sv', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('name_local', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('abbr_fi', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('abbr_scientific', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('height', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('width', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('flower_color', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('flowering_time', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('substrate', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('spacing', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('kasvimuseo', ['Species'])

        # Adding model 'Contact'
        db.create_table('kasvimuseo_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('apartment', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('kasvimuseo', ['Contact'])

        # Adding model 'Location'
        db.create_table('kasvimuseo_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('external_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('village', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('apartment', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('history', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('kasvimuseo', ['Location'])

        # Adding M2M table for field contacts on 'Location'
        db.create_table('kasvimuseo_location_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm['kasvimuseo.location'], null=False)),
            ('contact', models.ForeignKey(orm['kasvimuseo.contact'], null=False))
        ))
        db.create_unique('kasvimuseo_location_contacts', ['location_id', 'contact_id'])

        # Adding model 'Observation'
        db.create_table('kasvimuseo_observation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('external_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kasvimuseo.Location'])),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kasvimuseo.Species'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('characteristics', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('nickname', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('history', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('stories', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pictures', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('kasvimuseo', ['Observation'])

        # Adding model 'Plot'
        db.create_table('kasvimuseo_plot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('kasvimuseo', ['Plot'])

        # Adding model 'Bed'
        db.create_table('kasvimuseo_bed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kasvimuseo.Plot'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('kasvimuseo', ['Bed'])

        # Adding model 'Planting'
        db.create_table('kasvimuseo_planting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('observation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kasvimuseo.Observation'])),
            ('Bed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kasvimuseo.Bed'])),
            ('planting_date', self.gf('django.db.models.fields.DateField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('removal_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('kasvimuseo', ['Planting'])

        # Adding model 'Care'
        db.create_table('kasvimuseo_care', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('planting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kasvimuseo.Planting'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('kasvimuseo', ['Care'])


    def backwards(self, orm):
        
        # Deleting model 'Species'
        db.delete_table('kasvimuseo_species')

        # Deleting model 'Contact'
        db.delete_table('kasvimuseo_contact')

        # Deleting model 'Location'
        db.delete_table('kasvimuseo_location')

        # Removing M2M table for field contacts on 'Location'
        db.delete_table('kasvimuseo_location_contacts')

        # Deleting model 'Observation'
        db.delete_table('kasvimuseo_observation')

        # Deleting model 'Plot'
        db.delete_table('kasvimuseo_plot')

        # Deleting model 'Bed'
        db.delete_table('kasvimuseo_bed')

        # Deleting model 'Planting'
        db.delete_table('kasvimuseo_planting')

        # Deleting model 'Care'
        db.delete_table('kasvimuseo_care')


    models = {
        'kasvimuseo.bed': {
            'Meta': {'object_name': 'Bed'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Plot']", 'null': 'True'})
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
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kasvimuseo.Contact']", 'symmetrical': 'False'}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'village': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
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
            'Bed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kasvimuseo.Bed']"}),
            'Meta': {'object_name': 'Planting'},
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
