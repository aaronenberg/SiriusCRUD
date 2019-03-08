from ..models import Article
from django import template


register = template.Library()

@register.simple_tag
def get_absolute_url(article):
    return article.get_absolute_url(article)
