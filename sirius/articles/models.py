import datetime
import itertools
import os
import uuid
from django.conf import settings
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Article(models.Model):

    FALL = 'FA'
    WINTER = 'WI'
    SPRING = 'SP'
    SUMMER = 'SU'
    SEMESTER_CHOICES = BLANK_CHOICE_DASH + [
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    ]
    def current_year():
        return datetime.datetime.now().year

    YEAR_CHOICES = [] + BLANK_CHOICE_DASH
    for y in reversed(range(2000, (current_year()+1))):
            YEAR_CHOICES.append((y,y))

    author = models.ForeignKey(
        'users.BaseUser',
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('author')
    )
    title = models.CharField(_('title'), max_length=255, default='', blank=False)

    description = models.TextField(
        _('description'),
        max_length=512,
        blank=True,
        help_text=_("Type a description...")
    )

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

    semester = models.CharField(
        _('semester'),
        max_length=2,
        choices=SEMESTER_CHOICES,
        default=FALL, blank=True
    )
    year = models.PositiveSmallIntegerField(
        _('year'),
        choices=YEAR_CHOICES,
        default=current_year,
        blank=True,
        null=True
    )

    def get_absolute_url(self, article=None):
        if not article:
            return reverse('articles:article-detail', kwargs={'slug': self.slug})
        if not isinstance(article, Article):
            raise ValueError("{} is not of type {}".format(type(article), Article))
        if article.is_public:
            return reverse('articles:article-detail', kwargs={'slug': self.slug})
        return reverse('articles:draft-detail', kwargs={'slug': self.slug})


    def generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        slug = slugify(self.title)[:max_length]
        if not Article.objects.filter(slug=slug).exists():
            return slug
        for i in itertools.count(1):
            slug_truncated = slug[:max_length - len(str(i)) - 1]
            if not Article.objects.filter(slug="{}-{}".format(slug_truncated, i)).exists():
                return "{}-{}".format(slug_truncated, i)
        return

    def save(self, *args, **kwargs):
        self.slug = self.generate_slug()
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        if len(self.title) >= 75:
            return self.title[:72] + "..."
        return self.title


class ArticleMedia(models.Model):

    ANALYZED_DATA = 'AD'
    POSTER = 'PO'
    RAW_DATA = 'RD'
    REPORT = 'RE'
    OTHER = 'OT'
    ARTICLE_TYPES = BLANK_CHOICE_DASH + [
        (ANALYZED_DATA, 'Analyzed Data'),
        (POSTER, 'Poster'),
        (RAW_DATA, 'Raw Data'),
        (REPORT, 'Report'),
        (OTHER, 'Other'),
    ]

    # insert uuid to prevent renaming file when a file with same name already exists
    def upload_to(instance, filename):
        today = datetime.datetime.now().strftime("%Y%m%d")
        return 'uploads/{0}/{1}/{2}'.format(today, uuid.uuid4(), filename)

    article_media = models.FileField(_('file upload'), upload_to=upload_to)

    article_type = models.CharField(
        _('article type'),
        max_length=2,
        choices=ARTICLE_TYPES,
        help_text=_("Select the file type")
    )
    created = models.DateTimeField(auto_now_add=True)
    
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='media')

    # chop off relative path to Storage to get just the name of file
    @property
    def filename(self):
        return os.path.basename(self.article_media.name)

