import math
import re
import datetime
from django.core.validators import MaxValueValidator
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
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


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


def get_course_from_url(url):
    course_slug_pattern = re.compile('[A-Z]{2,4}\d{1,3}[A-Z]?')
    match = course_slug_pattern.search(url) 
    if match:
        slug = match.group()
        try:
            path = reverse('courses:course-detail', kwargs={'slug': slug})
        except NoReverseMatch:
            return None
        return Course.objects.get(slug=slug)
    else:
        return None


def flatten_formset_file_fields(formset):
    from .models import OutcomeMedia
    media = []
    for i, file_field in enumerate(formset.files.keys()):
        for fp in formset.files.getlist(file_field):
            outcome_type = formset.forms[i].cleaned_data['outcome_type']
            outcome = formset.forms[i].cleaned_data['outcome']
            media.append(OutcomeMedia(media=fp, outcome_type=outcome_type, outcome=outcome))
    return media
