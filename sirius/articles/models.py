import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Article(models.Model):

    RAW_DATA = 'RD'
    ANALYZED_DATA = 'AD'
    REPORT = 'RE'
    POSTER = 'PO'
    OTHER = 'OT'
    ARTICLE_TYPES = (
        (RAW_DATA, 'Raw Data'),
        (ANALYZED_DATA, 'Analyzed Data'),
        (REPORT, 'Report'),
        (POSTER, 'Poster'),
        (OTHER, 'Other'),
    )
    
    CHEMISTRY = 'CY'
    BIOLOGY = 'BY'
    CIVIL_ENGINEERING = 'CE'
    DISCIPLINES = (
        (CHEMISTRY, 'Chemistry'),
        (BIOLOGY, 'Biology'),
        (CIVIL_ENGINEERING, 'Civil Engineering'),
    )

    title = models.CharField(max_length=255, default='', blank=False)

    article_type = models.CharField(max_length=2, choices=ARTICLE_TYPES)

    description = models.TextField(max_length=512, blank=True)

    discipline = models.CharField(max_length=2, choices=DISCIPLINES)

    slug = models.SlugField(unique=True, editable=False)

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)


class ArticleMedia(models.Model):

    # file will be saved to MEDIA_ROOT/uploads/2019/02/16
    # file url will be MEDIA_URL/uploads/2019/02/16
    media = models.FileField(upload_to='uploads/%Y/%m/%d')

    created = models.DateTimeField(auto_now_add=True)
    
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='media')

    # chop off relative path to Storage to get just the name of file
    def filename(self):
        return os.path.basename(self.media.name)
