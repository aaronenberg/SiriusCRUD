# Generated by Django 2.1.7 on 2019-04-20 21:41

import developments.models
import developments.utils
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Development',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=99, verbose_name='title')),
                ('description', models.TextField(blank=True, help_text='Type a description...', max_length=2000, verbose_name='description')),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_public', models.BooleanField(default=True)),
                ('semester', models.CharField(blank=True, choices=[('', '---------'), ('FA', 'Fall'), ('WI', 'Winter'), ('SP', 'Spring'), ('SU', 'Summer')], default='FA', max_length=2, verbose_name='semester')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2000), developments.utils.max_value_current_year], verbose_name='year')),
            ],
        ),
        migrations.CreateModel(
            name='DevelopmentMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to=developments.models.DevelopmentMedia.upload_to, verbose_name='file upload')),
                ('development_type', models.CharField(blank=True, choices=[('', '---------'), ('SD', 'Analyzed Data'), ('PO', 'Poster'), ('RD', 'Raw Data'), ('RE', 'Report'), ('OT', 'Other')], default='', help_text='Select the file type', max_length=2, verbose_name='development type')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_public', models.BooleanField(default=False)),
                ('semester', models.CharField(blank=True, choices=[('', '---------'), ('FA', 'Fall'), ('WI', 'Winter'), ('SP', 'Spring'), ('SU', 'Summer')], default='FA', max_length=2, verbose_name='semester')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2000), developments.utils.max_value_current_year], verbose_name='year')),
            ],
        ),
    ]
