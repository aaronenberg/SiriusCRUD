from outcomes.utils import time_since as ts
from django import template


register = template.Library()

@register.simple_tag
def get_absolute_url(development):
    return development.get_absolute_url(development)

@register.simple_tag
def time_since(time):
    return ts(time)
