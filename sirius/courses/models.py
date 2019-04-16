from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Course(models.Model):

    BIOLOGY = 'BIO'
    CHEMISTRY = 'CHEM'
    CIVIL_ENGINEERING = 'CE'
    ENVIRONMENTAL_STUDIES = 'ENVS'
    GEOLOGY = 'GEOL'
    SUBJECT_CHOICES = BLANK_CHOICE_DASH + [
        (BIOLOGY, 'Biology'),
        (CHEMISTRY, 'Chemistry'),
        (CIVIL_ENGINEERING, 'Civil Engineering'),
        (ENVIRONMENTAL_STUDIES, 'Environmental Studies'),
        (GEOLOGY, 'Geology'),
    ]

    description = models.TextField(blank=True, max_length=2000)

    number = models.CharField(max_length=4)

    slug = models.SlugField(unique=True)
    
    subject = models.CharField(max_length=4, choices=SUBJECT_CHOICES)

    sections = ArrayField(
        models.PositiveSmallIntegerField(blank=True, null=True),
        blank=True,
        null=True
    )

    title = models.CharField(max_length=99)


    class Meta:
        unique_together = ("subject", "number")

    def get_absolute_url(self):
        return reverse('courses:course-detail', kwargs={'subject': self.subject, 'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = "{}{}".format(self.subject, self.number)
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} {1} - {2}".format(self.subject, self.number, self.title)
    

