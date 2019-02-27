import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Article(models.Model):

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

    author = models.ForeignKey('users.BaseUser', on_delete=models.CASCADE, related_name='articles')

    title = models.CharField(max_length=255, default='', blank=False)

    article_type = models.CharField(max_length=2, choices=ARTICLE_TYPES)

    description = models.TextField(max_length=512, blank=True)

    subject = models.CharField(max_length=2, choices=SUBJECTS)

    slug = models.SlugField(unique=True, editable=False)

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)


class ArticleMedia(models.Model):

    # file will be saved to MEDIA_ROOT/uploads/2019/02/16
    # file url will be MEDIA_URL/uploads/2019/02/16
    article_media = models.FileField(upload_to='uploads/%Y/%m/%d')

    created = models.DateTimeField(auto_now_add=True)
    
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='media')

    # chop off relative path to Storage to get just the name of file
    def filename(self):
        return os.path.basename(self.article_media.name)
