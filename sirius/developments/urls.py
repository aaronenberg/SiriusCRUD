from django.urls import path
from . import views

app_name = 'developments'

urlpatterns = [
    path('developments/', views.DevelopmentListView.as_view(), name='development-list'),
    # TODO: fix so that a development with title "drafts" can be resolved
    path('developments/drafts/', views.DraftListView.as_view(), name='draft-list'),
    path(
        'developments/<slug:slug>/',
        views.DevelopmentDetailView.as_view(),
        name='development-detail'
    ),
    path(
        'developments/<slug:slug>/edit/',
        views.DevelopmentUpdateView.as_view(),
        name='development-update'
    ),
    path('developments/create/new/', views.DevelopmentCreateView.as_view(), name='development-create'),
    #path('developments/search/results/', views.SearchResultsView.as_view(), name='search-results'),
    path('developments/drafts/<slug:slug>/', views.DraftDetailView.as_view(), name='draft-detail'),
    path('developments/drafts/<slug:slug>/edit/', views.DraftUpdateView.as_view(), name='draft-update'),
]

