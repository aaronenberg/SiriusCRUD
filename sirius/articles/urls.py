from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/new/', views.ArticleCreateView.as_view(), name='article-create'),
    path('drafts/', views.DraftListView.as_view(), name='draft-list'),
    path('search/', views.SearchPageView.as_view(), name='search'),
    path('search/results/', views.SearchResultsView.as_view(), name='search-results'),
    path('drafts/<slug:slug>/', views.DraftDetailView.as_view(), name='draft-detail'),
    path('drafts/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='draft-update'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article-update'),
    path('submissions/', views.SubmissionListView.as_view(), name='submission-list'),
    path('submissions/<slug:slug>/', views.SubmissionDetailView.as_view(), name='submission-detail'),
    path('ajax/get-sections/', views.get_course_sections, name='ajax-get-sections'),
]

