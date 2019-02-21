from rest_framework import serializers
from .models import Article, Post

class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('article',)

class PostSerializer(serializers.HyperlinkedModelSerializer):


    articles = ArticleSerializer(many=True)

    url = serializers.HyperlinkedIdentityField(
        view_name='post-detail',
        lookup_field='slug',
    )

    class Meta:
        model = Post
        fields = (
            'articles', 'title', 'article_type', 'description', 'discipline',
            'slug', 'created', 'modified', 'url',
        )

    def create(self, validated_data):
        article_data = validated_data.pop('articles')
        post = Post.objects.create(**validated_data)
        Article.objects.create(post=post, **article_data)
        return post
