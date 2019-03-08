from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/new/', views.ArticleCreateView.as_view(), name='article-create'),
    path('drafts/', views.DraftListView.as_view(), name='draft-list'),
    path('drafts/<slug:slug>/', views.DraftDetailView.as_view(), name='draft-detail'),
    path('drafts/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='draft-update'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article-update'),
]

