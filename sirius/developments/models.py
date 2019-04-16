import datetime
import itertools
import os
import uuid
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .utils import max_value_current_year, current_semester, current_year


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


class Development(models.Model):

    author = models.ForeignKey(
        'users.BaseUser',
        on_delete=models.CASCADE,
        related_name='developments',
        verbose_name=_('author')
    )

    title = models.CharField(_('title'), max_length=99, blank=False)

    description = models.TextField(
        _('description'),
        max_length=2000,
        blank=True,
        help_text=_("Type a description...")
    )

    slug = models.SlugField(unique=True, editable=False)

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=True)

    semester = models.CharField(
        _('semester'),
        max_length=2,
        choices=SEMESTER_CHOICES,
        default=FALL,
        blank=True
    )

    year = models.PositiveSmallIntegerField(
        _('year'),
        validators=[MinValueValidator(2000), max_value_current_year],
        blank=True,
        null=True
    )

    def get_absolute_url(self, development=None):
        if development:
            if not isinstance(development, Development):
                raise ValueError("{} is not of type {}".format(type(development), Development))
            if development.is_public:
                return reverse('developments:development-detail', kwargs={'slug': development.slug})
            return reverse('developments:draft-detail', kwargs={'slug': development.slug})
        elif self.is_public:
            return reverse('developments:development-detail', kwargs={'slug': self.slug})
        return reverse('developments:draft-detail', kwargs={'slug': self.slug})

    def generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        slug = slugify(self.title)[:max_length]
        if not Development.objects.filter(slug=slug).exists():
            return slug
        for i in itertools.count(1):
            slug_truncated = slug[:max_length - len(str(i)) - 1]
            if not Development.objects.filter(slug="{}-{}".format(slug_truncated, i)).exists():
                return "{}-{}".format(slug_truncated, i)
        return

    def save(self, *args, **kwargs):
        self.slug = self.generate_slug()
        super(Development, self).save(*args, **kwargs)

    def __str__(self):
        if len(self.title) >= 75:
            return self.title[:72] + "..."
        return self.title


class DevelopmentMedia(models.Model):

    ANALYZED_DATA = 'SD'
    POSTER = 'PO'
    RAW_DATA = 'RD'
    REPORT = 'RE'
    OTHER = 'OT'
    DEVELOPMENT_TYPES = BLANK_CHOICE_DASH + [
        (ANALYZED_DATA, 'Analyzed Data'),
        (POSTER, 'Poster'),
        (RAW_DATA, 'Raw Data'),
        (REPORT, 'Report'),
        (OTHER, 'Other'),
    ]

    development = models.ForeignKey('Development', on_delete=models.CASCADE, related_name='development_media')

    # insert uuid to prevent renaming file when a file with same name already exists
    def upload_to(instance, filename):
        today = datetime.datetime.now().strftime("%Y%m%d")
        return 'uploads/{0}/{1}/{2}'.format(today, uuid.uuid4(), filename)

    media = models.FileField(_('file upload'), upload_to=upload_to)

    development_type = models.CharField(
        _('development type'),
        max_length=2,
        choices=DEVELOPMENT_TYPES,
        default="",
        blank=True,
        help_text=_("Select the file type")
    )

    author = models.ForeignKey(
        'users.BaseUser',
        on_delete=models.CASCADE,
        related_name='development_uploads',
        verbose_name=_('author')
    )

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)

    semester = models.CharField(
        _('semester'),
        max_length=2,
        choices=SEMESTER_CHOICES,
        default=FALL,
        blank=True
    )
    year = models.PositiveSmallIntegerField(
        _('year'),
        validators=[MinValueValidator(2000), max_value_current_year],
        blank=True,
        null=True
    )
    
    # chop off relative path to Storage to get just the name of file
    @property
    def filename(self):
        return os.path.basename(self.media.name)

    def save(self, *args, **kwargs):
        self.year = current_year()
        self.semester = current_semester()
        super(DevelopmentMedia, self).save(*args, **kwargs)

