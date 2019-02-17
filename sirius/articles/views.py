from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import ArticleSerializer
from .models import Article


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-upload_datetime')
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]
    # lookup field must be set on both view and serializer
    # when using HyperlinkedModelSerializer
    lookup_field = 'slug'
