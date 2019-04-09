from django.urls import path
from . import views


app_name = 'outcomes'

urlpatterns = [
    path('outcomes/', views.OutcomeListView.as_view(), name='outcome-list'),
    path(
        'outcomes/<slug:slug>/',
        views.OutcomeMediaUpdateView.as_view(),
        name='outcome-media-update'
    ),
    path(
        'outcomes/<slug:slug>/edit/',
        views.OutcomeUpdateView.as_view(),
        name='outcome-update'
    ),
    path(
        'outcomes/<slug:slug>/submissions/',
        views.OutcomeSubmissionsUpdateView.as_view(),
        name='outcome-submissions-update'
    ),
    path('outcomes/create/new/', views.OutcomeCreateView.as_view(), name='outcome-create'),
    path('drafts/', views.DraftListView.as_view(), name='draft-list'),
    path('search/results/', views.SearchResultsView.as_view(), name='search-results'),
    path('drafts/<slug:slug>/', views.DraftDetailView.as_view(), name='draft-detail'),
    path('drafts/<slug:slug>/edit/', views.DraftUpdateView.as_view(), name='draft-update'),
    path('ajax/get-sections/', views.get_course_sections, name='ajax-get-sections'),
]

