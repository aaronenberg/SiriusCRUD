from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Course(models.Model):

    BIOLOGY = 'BI'
    CHEMISTRY = 'CH'
    CIVIL_ENGINEERING = 'CE'
    ENVIRONMENTAL_STUDIES = 'ES'
    GEOLOGY = 'GE'
    SUBJECTS = (
        (BIOLOGY, 'BIO'),
        (CHEMISTRY, 'CHEM'),
        (CIVIL_ENGINEERING, 'CE'),
        (ENVIRONMENTAL_STUDIES, 'ENVS'),
        (GEOLOGY, 'GEOL'),
    )

    description = models.TextField(blank=True)

    is_public = models.BooleanField(default=True)

    number = models.CharField(max_length=4)

    slug = models.SlugField(editable=False)
    
    subject = models.CharField(max_length=2, choices=SUBJECTS)

    section = ArrayField(models.PositiveSmallIntegerField())

    title = models.CharField(max_length=99)

    class Meta:
        unique_together = ("subject", "number")

    #def get_section_display(self):
    #    return "{:02d}".format(self.section.number)

    def get_absolute_url(self):
        return reverse('course-detail-section-list', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = "{}{}".format(self.get_subject_display(), self.number)
        super(Course, self).save(*args, **kwargs)

    

