# Generated by Django 2.1.7 on 2019-04-16 02:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=2000)),
                ('number', models.CharField(max_length=4)),
                ('slug', models.SlugField(unique=True)),
                ('subject', models.CharField(choices=[('', '---------'), ('BIO', 'Biology'), ('CHEM', 'Chemistry'), ('CE', 'Civil Engineering'), ('ENVS', 'Environmental Studies'), ('GEOL', 'Geology')], max_length=4)),
                ('sections', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(blank=True, null=True), blank=True, null=True, size=None)),
                ('title', models.CharField(max_length=99)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('subject', 'number')},
        ),
    ]
