from django.urls import path
from . import views

app_name = 'developments'

urlpatterns = [
    path('developments/', views.DevelopmentListView.as_view(), name='development-list'),
    path('developments/<slug:slug>/', views.DevelopmentDetailView.as_view(),name='development-detail'),
    path('developments/<slug:slug>/edit/', views.DevelopmentUpdateView.as_view(), name='development-update'),
    path('search/developments/results/', views.SearchResultsView.as_view(), name='search-results'),
    path('developments/create/new/', views.DevelopmentCreateView.as_view(), name='development-create'),
    path('drafts/developments/', views.DraftListView.as_view(), name='draft-list'),
    path('drafts/developments/<slug:slug>/', views.DraftDetailView.as_view(), name='draft-detail'),
    path('drafts/developments/<slug:slug>/edit/', views.DraftUpdateView.as_view(), name='draft-update'),
]

