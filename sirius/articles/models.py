from django.db import models
from django.contrib.postgres.fields import ArrayField
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

    # file will be saved to MEDIA_ROOT/uploads/2019/02/16
    # file url will be MEDIA_URL/uploads/2019/02/16
    article = models.FileField(upload_to='uploads/%Y/%m/%d')

    title = models.CharField(max_length=32, default='filename', blank=False)

    article_type = models.CharField(max_length=2, choices=ARTICLE_TYPES)

    description = models.TextField(max_length=512, blank=True)

    discipline = models.CharField(max_length=2, choices=DISCIPLINES)

    slug = models.SlugField(unique=True, editable=False)
    upload_datetime = models.DateTimeField(auto_now=True)

    #revisions = ArrayField(models.FileField(upload_to='uploads/%Y/%m/%d'), default=list)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        #self.revisions.append(self.article)
        super(Article, self).save(*args, **kwargs)
