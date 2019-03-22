# Generated by Django 2.1.7 on 2019-03-18 02:57

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
                ('description', models.TextField(blank=True)),
                ('number', models.CharField(max_length=4)),
                ('slug', models.SlugField(editable=False, primary_key=True, serialize=False)),
                ('subject', models.CharField(choices=[('', '---------'), ('BIO', 'BIOLOGY'), ('CHEM', 'CHEMISTRY'), ('CE', 'CIVIL ENGINEERING'), ('ENVS', 'ENVIRONMENTAL STUDIES'), ('GEOL', 'GEOLOGY')], max_length=4)),
                ('sections', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(blank=True, null=True), blank=True, null=True, size=None)),
                ('title', models.CharField(max_length=99)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('subject', 'number')},
        ),
    ]
