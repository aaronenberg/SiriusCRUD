import datetime
import os
import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Article(models.Model):

    BIOLOGY = 'BI'
    CHEMISTRY = 'CH'
    CIVIL_ENGINEERING = 'CE'
    ENVIRONMENTAL_STUDIES = 'EN'
    GEOLOGY = 'GE'
    SUBJECTS = (
        (BIOLOGY, 'Biology'),
        (CHEMISTRY, 'Chemistry'),
        (CIVIL_ENGINEERING, 'Civil Engineering'),
        (ENVIRONMENTAL_STUDIES, 'Environmental Studies'),
        (GEOLOGY, 'Geology'),
    )
    FALL = 'FA'
    WINTER = 'WI'
    SPRING = 'SP'
    SUMMER = 'SU'
    SEMESTER_CHOICES = (
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    )
    def current_year():
        return datetime.datetime.now().year

    YEAR_CHOICES = []
    for y in range(2000, (current_year()+1)):
            YEAR_CHOICES.append((y,y))

    author = models.ForeignKey(
        'users.BaseUser',
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('author')
    )
    title = models.CharField(_('title'), max_length=255, default='', blank=False)

    description = models.TextField(_('description'), max_length=512, blank=True)

    subject = models.CharField(_('subject'), max_length=2, choices=SUBJECTS, blank=True)

    slug = models.SlugField(unique=True, editable=False)

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('course'),
        blank=True,
        null=True
    )
    section = models.PositiveSmallIntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=True)

    semester = models.CharField(_('semester'), max_length=2, choices=SEMESTER_CHOICES, default=FALL, blank=True)

    year = models.PositiveSmallIntegerField(_('year'), choices=YEAR_CHOICES, default=current_year, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('articles:article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class ArticleMedia(models.Model):

    ANALYZED_DATA = 'AD'
    POSTER = 'PO'
    RAW_DATA = 'RD'
    REPORT = 'RE'
    OTHER = 'OT'
    ARTICLE_TYPES = (
        (ANALYZED_DATA, 'Analyzed Data'),
        (POSTER, 'Poster'),
        (RAW_DATA, 'Raw Data'),
        (REPORT, 'Report'),
        (OTHER, 'Other'),
    )
    article_type = models.CharField(_('article type'), max_length=2, choices=ARTICLE_TYPES)

    # insert uuid to prevent renaming file when a file with same name already exists
    def upload_to(instance, filename):
        today = datetime.datetime.now().strftime("%Y%m%d")
        return 'uploads/{0}/{1}/{2}'.format(today, uuid.uuid4(), filename)

    article_media = models.FileField(upload_to=upload_to)

    created = models.DateTimeField(auto_now_add=True)
    
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='media')

    # chop off relative path to Storage to get just the name of file
    @property
    def filename(self):
        return os.path.basename(self.article_media.name)

