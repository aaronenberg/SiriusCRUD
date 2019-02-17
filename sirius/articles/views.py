from rest_framework import viewsets
from .serializers import ArticleSerializer
from .models import Article


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-upload_datetime')
    serializer_class = ArticleSerializer
    # lookup field must be set on both view and serializer
    # when using HyperlinkedModelSerializer
    lookup_field = 'slug'
