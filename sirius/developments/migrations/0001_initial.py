# Generated by Django 2.2.2 on 2019-06-28 18:52

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
                ('semester', models.CharField(blank=True, choices=[('', '---------'), ('Fall', 'Fall'), ('Winter', 'Winter'), ('Spring', 'Spring'), ('Summer', 'Summer')], default='Fall', max_length=6, verbose_name='semester')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2000), developments.utils.max_value_current_year], verbose_name='year')),
            ],
        ),
        migrations.CreateModel(
            name='DevelopmentMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to=developments.models.DevelopmentMedia.upload_to, verbose_name='file upload')),
                ('upload_directory', models.CharField(blank=True, default='', max_length=2048)),
                ('development_type', models.CharField(blank=True, choices=[('', '---------'), ('AG', 'Agenda'), ('AS', 'Assessment'), ('PE', 'People'), ('PR', 'Presentation'), ('OT', 'Other')], default='', help_text='Select the file type', max_length=2, verbose_name='development type')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_public', models.BooleanField(default=False)),
                ('semester', models.CharField(blank=True, choices=[('', '---------'), ('Fall', 'Fall'), ('Winter', 'Winter'), ('Spring', 'Spring'), ('Summer', 'Summer')], default='Fall', max_length=6, verbose_name='semester')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2000), developments.utils.max_value_current_year], verbose_name='year')),
            ],
        ),
    ]
