import datetime
import itertools
import os
import uuid

from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.urls import reverse
from django.utils.text import slugify, get_valid_filename
from django.utils.translation import gettext_lazy as _

from storages.utils import safe_join
from .utils import max_value_current_year, current_semester, current_year


class Development(models.Model):

    FALL = 'Fall'
    WINTER = 'Winter'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    SEMESTER_CHOICES = BLANK_CHOICE_DASH + [
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    ]

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
        max_length=6,
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

    def __str__(self):
        if len(self.title) >= 75:
            return self.title[:72] + "..."
        return self.title


class DevelopmentMedia(models.Model):

    FALL = 'Fall'
    WINTER = 'Winter'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    SEMESTER_CHOICES = BLANK_CHOICE_DASH + [
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    ]

    AGENDA = 'AG'
    ASSESSMENT = 'AS'
    PEOPLE = 'PE'
    PRESENTATION = 'PR'
    OTHER = 'OT'
    DEVELOPMENT_TYPES = BLANK_CHOICE_DASH + [
        (AGENDA, 'Agenda'),
        (ASSESSMENT, 'Assessment'),
        (PEOPLE, 'People'),
        (PRESENTATION, 'Presentation'),
        (OTHER, 'Other'),
    ]

    UPLOADS_ROOT_DIR = 'uploads/development'

    development = models.ForeignKey('Development', on_delete=models.CASCADE, related_name='development_media')

    def upload_to(instance, filename):
        return safe_join(
            instance.UPLOADS_ROOT_DIR,
            instance.development.slug,
            instance.upload_directory,
            instance.filename
        )

    media = models.FileField(_('file upload'), upload_to=upload_to)

    upload_directory = models.CharField(max_length=2048, default='', blank=True)

    development_type = models.CharField(
        _('development type'),
        max_length=2,
        choices=DEVELOPMENT_TYPES,
        default='',
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
        max_length=6,
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
        return get_valid_filename(os.path.basename(self.media.name))

    def rename_dup(self):
        max_length = self._meta.get_field('media').max_length
        name, ext = os.path.splitext(self.media.name)
        for i in itertools.count(1):
            dup_count_str = '_%s' % i
            name_truncated = name[:max_length - len(dup_count_str) - len(ext)]
            file_path = safe_join(
                self.UPLOADS_ROOT_DIR,
                os.path.dirname(str(self)),
                get_valid_filename(name + dup_count_str + ext)
            )
            if not default_storage.exists(file_path):
                return os.path.basename(file_path)

    def save(self, *args, **kwargs):
        self.year = current_year()
        self.semester = current_semester()
        super(DevelopmentMedia, self).save(*args, **kwargs)

    def __str__(self):
        return safe_join(
            self.development.slug,
            self.upload_directory,
            self.filename
        )
