from ..models import Article
from django import template


register = template.Library()

@register.simple_tag
def get_absolute_url(article):
    return article.get_absolute_url(article)

@register.simple_tag
def time_since(time):
    return Article.time_since(Article, time)
