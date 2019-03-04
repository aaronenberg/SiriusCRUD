from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('drafts', views.DraftListView.as_view(), name='draft-list'),
    path('new', views.ArticleCreateView.as_view(), name='article-create'),
	path('search/', views.SearchPageView.as_view(), name='search'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('<slug:slug>/edit', views.ArticleUpdateView.as_view(), name='article-update'),
]

