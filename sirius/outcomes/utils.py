import math
import datetime
from django.core.validators import MaxValueValidator
from django.utils import timezone


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
