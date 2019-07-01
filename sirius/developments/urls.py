from django.urls import path
from . import views

app_name = 'developments'

urlpatterns = [
    path('development', views.DevelopmentListView.as_view(), name='development-list'),
    path('development/<slug:slug>', views.DevelopmentDetailView.as_view(),name='development-detail'),
    path('development/<slug:slug>/edit', views.DevelopmentUpdateView.as_view(), name='development-update'),
    path('search/development/results', views.SearchResultsView.as_view(), name='search-results'),
    path('development/create/new', views.DevelopmentCreateView.as_view(), name='development-create'),
    path('drafts/development', views.DraftListView.as_view(), name='draft-list'),
    path('drafts/development/<slug:slug>', views.DraftDetailView.as_view(), name='draft-detail'),
    path('drafts/development/<slug:slug>/edit', views.DraftUpdateView.as_view(), name='draft-update'),
    path('ajax/development/get-development-media', views.get_development_media, name='ajax-get-development-media'),
]

