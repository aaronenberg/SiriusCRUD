from rest_framework import viewsets
from .serializers import PostSerializer
from .models import Article, Post


class PostViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all().order_by('modified')

    serializer_class = PostSerializer

    # lookup field must be set on both view and serializer
    # when using HyperlinkedModelSerializer
    lookup_field = 'slug'
