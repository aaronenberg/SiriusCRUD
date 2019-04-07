import datetime
import itertools
import os
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .utils import max_value_current_year, current_year, current_semester


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


class Outcome(models.Model):
    author = models.ForeignKey(
        'users.BaseUser',
        on_delete=models.CASCADE,
        related_name='outcomes',
        verbose_name=_('author')
    )
    title = models.CharField(_('title'), max_length=255, blank=False)

    description = models.TextField(
        _('description'),
        max_length=512,
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

    def save(self, *args, **kwargs):
        self.slug = self.generate_slug()
        super(Outcome, self).save(*args, **kwargs)

    def __str__(self):
        if len(self.title) >= 75:
            return self.title[:72] + "..."
        return self.title


class OutcomeMedia(models.Model):

    ANALYZED_DATA = 'AD'
    POSTER = 'PO'
    RAW_DATA = 'RD'
    REPORT = 'RE'
    OTHER = 'OT'
    OUTCOME_TYPES = BLANK_CHOICE_DASH + [
        (ANALYZED_DATA, 'Analyzed Data'),
        (POSTER, 'Poster'),
        (RAW_DATA, 'Raw Data'),
        (REPORT, 'Report'),
        (OTHER, 'Other'),
    ]

    outcome = models.ForeignKey('Outcome', on_delete=models.CASCADE, related_name='media')

    # insert uuid to prevent renaming file when a file with same name already exists
    def upload_to(instance, filename):
        today = datetime.datetime.now().strftime("%Y%m%d")
        return 'uploads/{0}/{1}/{2}'.format(today, uuid.uuid4(), filename)

    media = models.FileField(_('file upload'), upload_to=upload_to)

    outcome_type = models.CharField(
        _('outcome type'),
        max_length=2,
        choices=OUTCOME_TYPES,
        default="",
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

    section = models.PositiveSmallIntegerField(blank=True, null=True)

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
        super(OutcomeMedia, self).save(*args, **kwargs)

