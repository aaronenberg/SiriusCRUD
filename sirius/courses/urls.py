from django.urls import path
from . import views


app_name = 'courses'

urlpatterns = [
    path('courses/', views.SubjectListView.as_view(), name='subject-list'),
    path('courses/<str:subject>/', views.SubjectCoursesListView.as_view(), name='subject-courses-list'),
    path('courses/create/new/', views.CourseCreateView.as_view(), name='course-create'),
    path('courses/<str:subject>/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<str:subject>/<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),
    path('courses/<str:subject>/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course-update'),
    path('ajax/courses/get-outcome-media/', views.get_outcome_media, name='ajax-get-outcome-media'),
]

