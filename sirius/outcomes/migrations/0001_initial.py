# Generated by Django 2.1.7 on 2019-04-09 00:30

import django.core.validators
from django.db import migrations, models
import outcomes.models
import outcomes.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, help_text='Type a description...', max_length=512, verbose_name='description')),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('section', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_public', models.BooleanField(default=True)),
                ('semester', models.CharField(blank=True, choices=[('', '---------'), ('FA', 'Fall'), ('WI', 'Winter'), ('SP', 'Spring'), ('SU', 'Summer')], default='FA', max_length=2, verbose_name='semester')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2000), outcomes.utils.max_value_current_year], verbose_name='year')),
            ],
        ),
        migrations.CreateModel(
            name='OutcomeMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to=outcomes.models.OutcomeMedia.upload_to, verbose_name='file upload')),
                ('outcome_type', models.CharField(blank=True, choices=[('', '---------'), ('AD', 'Analyzed Data'), ('PO', 'Poster'), ('RD', 'Raw Data'), ('RE', 'Report'), ('OT', 'Other')], default='', help_text='Select the file type', max_length=2, verbose_name='outcome type')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_public', models.BooleanField(default=False)),
                ('section', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('semester', models.CharField(blank=True, choices=[('', '---------'), ('FA', 'Fall'), ('WI', 'Winter'), ('SP', 'Spring'), ('SU', 'Summer')], default='FA', max_length=2, verbose_name='semester')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2000), outcomes.utils.max_value_current_year], verbose_name='year')),
            ],
        ),
    ]