from ..utils import time_since as ts
from django import template


register = template.Library()

@register.simple_tag
def get_absolute_url(outcome):
    return outcome.get_absolute_url(outcome)

@register.simple_tag
def time_since(time):
    return ts(time)
