import datetime
import itertools
import os
import uuid

from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.urls import reverse
from django.utils.text import slugify, get_valid_filename
from django.utils.translation import gettext_lazy as _

from storages.utils import safe_join
from .utils import max_value_current_year, current_year, current_semester


class Outcome(models.Model):

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
        related_name='outcomes',
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

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        related_name='outcomes',
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

    def get_absolute_url(self, outcome=None):
        if outcome:
            if not isinstance(outcome, Outcome):
                raise ValueError("{} is not of type {}".format(type(outcome), Outcome))
            if outcome.is_public:
                return reverse('outcomes:outcome-media-update', kwargs={'slug': outcome.slug})
            return reverse('outcomes:draft-detail', kwargs={'slug': outcome.slug})
        elif self.is_public:
            return reverse('outcomes:outcome-media-update', kwargs={'slug': self.slug})
        return reverse('outcomes:draft-detail', kwargs={'slug': self.slug})

    def generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        slug = slugify(self.title)[:max_length]
        if not Outcome.objects.filter(slug=slug).exists():
            return slug
        for i in itertools.count(1):
            slug_truncated = slug[:max_length - len(str(i)) - 1]
            if not Outcome.objects.filter(slug="{}-{}".format(slug_truncated, i)).exists():
                return "{}-{}".format(slug_truncated, i)
        return

    def __str__(self):
        if len(self.title) >= 75:
            return self.title[:72] + "..."
        return self.title


class OutcomeMedia(models.Model):

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
    ANALYZED_DATA = 'AD'
    RAW_DATA = 'RD'
    CURRICULUM = 'CU'
    OUTCOME_TYPES = BLANK_CHOICE_DASH + [
        (RAW_DATA, 'Raw Data'),
        (ANALYZED_DATA, 'Analyzed Data'),
        (CURRICULUM, 'Curriculum'),
    ]

    UNPRIVILEGED_OUTCOME_TYPES = BLANK_CHOICE_DASH + [
        (RAW_DATA, 'Raw Data'),
        (ANALYZED_DATA, 'Analyzed Data'),
    ]

    UPLOADS_ROOT_DIR = 'uploads/outcomes' 

    outcome = models.ForeignKey('Outcome', on_delete=models.CASCADE, related_name='media')

    def upload_to(instance, filename):
        return safe_join(
            instance.UPLOADS_ROOT_DIR,
            instance.outcome.slug,
            instance.upload_directory,
            instance.filename
        )

    media = models.FileField(_('file upload'), upload_to=upload_to)

    upload_directory = models.CharField(max_length=2048, default='', blank=True)

    outcome_type = models.CharField(
        _('outcome type'),
        max_length=2,
        choices=OUTCOME_TYPES,
        default='',
        blank=True,
        help_text=_("Select the file type")
    )

    author = models.ForeignKey(
        'users.BaseUser',
        on_delete=models.CASCADE,
        related_name='uploads',
        verbose_name=_('author')
    )

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)

    is_delete = models.BooleanField(default=False)

    section = models.PositiveSmallIntegerField(blank=True, null=True)

    semester = models.CharField(
        _('semester'),
        max_length=6,
        choices=SEMESTER_CHOICES,
        blank=True,
        null=True
    )

    year = models.PositiveSmallIntegerField(
        _('year'),
        validators=[MinValueValidator(2000), max_value_current_year],
        blank=True,
        null=True
    )

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
        if self.outcome_type == OutcomeMedia.CURRICULUM:
            self.semester = None
            self.year = None
        else:
            self.year = current_year()
            self.semester = current_semester()
        super(OutcomeMedia, self).save(*args, **kwargs)

    def __str__(self):
        return safe_join(
            self.outcome.slug,
            self.upload_directory,
            self.filename
        )
