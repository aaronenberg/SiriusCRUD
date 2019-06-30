import datetime
import math
import os.path
import re

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3StorageFile
from storages.utils import safe_join

from courses.models import Course


def time_since(time):
    now = timezone.now()
    diff = now - time
    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        seconds = diff.seconds
        if seconds <= 1:
            return "just now"
        else:
            return str(seconds) + " seconds ago"
    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        minutes = math.floor(diff.seconds/60)
        if minutes == 1:
            return str(minutes) + " minute ago"
        else:
            return str(minutes) + " minutes ago"
    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        hours = math.floor(diff.seconds/3600)
        if hours == 1:
            return str(hours) + " hour ago"
        else:
            return str(hours) + " hours ago"
    if diff.days >= 1 and diff.days < 30:
        days = diff.days
        if days == 1:
            return str(days) + " day ago"
        else:
            return str(days) + " days ago"
    if diff.days >= 30 and diff.days < 365:
        months = math.floor(diff.days/30)
        if months == 1:
            return str(months) + " month ago"
        else:
            return str(months) + " months ago"
    if diff.days >= 365:
        years = math.floor(diff.days/365)
        if years == 1:
            return str(years) + " year ago"
        else:
            return str(years) + " years ago"


def current_year():
    return datetime.date.today().year


def current_semester():
    FALL = 'Fall'
    WINTER = 'Winter'
    SPRING = 'Spring'
    SUMMER = 'Summer'

    today = datetime.date.today()

    if today.month >= 1 and today.month <= 5:
        if today.month == 1 and today.day <= 14:
            return WINTER
        if today.month == 5 and today.day >= 23:
                return SUMMER
        return SPRING

    if today.month >= 8 and today.month <= 12:
        if today.month == 8 and today.day <= 21:
            return SUMMER
        if today.month == 12 and today.day >= 13:
                return WINTER
        return FALL
    return SUMMER


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


def get_course_from_url(url):
    if url and reverse('courses:subject-list') in url:
        course_slug_from_path = url.rstrip('/').split('/')[-1]
        try:
            course = Course.objects.get(slug=course_slug_from_path)
        except Course.DoesNotExist:
            return None
    else:
        return None
    return course.pk


def flatten_formset_file_fields(formset):
    from .models import OutcomeMedia
    media = []
    id_match = re.compile('-([0-9]+)-')
    for file_field in formset.files.keys():
        form_key = id_match.search(file_field)
        if not form_key:
            continue
        form_key = int(form_key.groups()[0])
        for idx, fp in enumerate(formset.files.getlist(file_field)):
            if not isinstance(fp, File):
                continue
            outcome_type = formset.forms[form_key].cleaned_data['outcome_type']
            outcome = formset.forms[form_key].cleaned_data['outcome']
            upload_directory = ''
            if isinstance(fp, S3Boto3StorageFile):
                upload_path = os.path.join(default_storage.location, settings.S3FILE_UPLOAD_PATH) + '/'
                try:
                    upload_directory = os.path.dirname(
                        formset.data.getlist(file_field)[idx]
                    ).split(upload_path, 1)[1].split('/', 1)[1]  # removes S3 upload path+base64
                except IndexError:
                    pass
            media.append(
                OutcomeMedia(
                    media=fp,
                    upload_directory=upload_directory,
                    outcome_type=outcome_type,
                    outcome=outcome
                )
            )
    return media


def update_files_formset(formset):
    '''Save media if it's not being updated, otherwise delete original before update with new.
       Also delete files attached to forms that are marked for deletion
    '''
    uploaded_file_fields = list(formset.files.keys())
    id_match = re.compile('-([0-9]+)-')
    for form in formset:
        if form.instance.id is not None:
            # if FieldFile then existing media is still valid, else it was replaced by a new upload
            if isinstance(form.cleaned_data['media'], FieldFile):
                form.save()
                uploaded_file_fields.remove(form.prefix + '-media')

    for file_field in uploaded_file_fields:
        files = formset.files.getlist(file_field)
        if not files:
            continue
        form_key = int(id_match.search(file_field).groups()[0])
        form = formset.forms[form_key]
        if form.cleaned_data['DELETE'] == True:
            formset.files.setlist(file_field, [])
            continue
        outcomemedia = form.cleaned_data.get('id')
        if not outcomemedia:
            continue
        media = files.pop()
        formset.files.setlist(file_field, files)
        if isinstance(media, (UploadedFile, S3Boto3StorageFile)):
            outcomemedia.media.delete()
            outcomemedia = form.save(commit=False)
            outcomemedia.media.save(media.name, media)


def filename(media):
    return os.path.basename(media.name)


def prepare_search_term(term):
    """Sanitize the input term for a search using postgres to_tsquery.

    Cleans a search string to something acceptable for use with to_tsquery.
    Appends ':*' so that partial matches will also be returned.

    Args:
        term: the search term to be cleaned and prepared

    Returns:
        the prepared search string
    """

    query = re.sub(r'[!\'()|&]', ' ', term).strip()
    if query:
        query = re.sub(r'\s+', ' & ', query)
        query += ':*'

    return query

