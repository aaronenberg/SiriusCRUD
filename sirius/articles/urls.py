from django.urls import path

from . import views

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/new/', views.ArticleCreateView.as_view(), name='article-create'),
    path('articles/<slug:slug>/', views.ArticleDetail.as_view(), name='article-detail'),
]

