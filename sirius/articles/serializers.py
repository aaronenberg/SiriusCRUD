from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='article-detail',
        lookup_field='slug',
    )
    class Meta:
        model = Article
        fields = (
            'article', 'title', 'article_type', 'description', 'discipline',
            'slug', 'upload_datetime', 'url',
        )
