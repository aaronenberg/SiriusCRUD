from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/drafts', views.DraftListView.as_view(), name='draft-list'),
    path('articles/new/', views.ArticleCreateView.as_view(), name='article-create'),
    path('articles/edit/<slug:slug>', views.ArticleUpdateView.as_view(), name='article-update'),
    path('articles/<slug:slug>/', views.ArticleDetail.as_view(), name='article-detail'),
]

