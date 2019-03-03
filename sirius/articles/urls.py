from django.urls import path
from . import views
from django_filters.views import FilterView
from .filters import ArticleFilter

app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('drafts', views.DraftListView.as_view(), name='draft-list'),
    path('new', views.ArticleCreateView.as_view(), name='article-create'),
	path('search/', FilterView.as_view(filterset_class=ArticleFilter), name='search'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('<slug:slug>/edit', views.ArticleUpdateView.as_view(), name='article-update'),
]

