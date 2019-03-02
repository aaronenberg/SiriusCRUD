from django.urls import path
from . import views


app_name = 'courses'

urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/new/', views.CourseCreateView.as_view(), name='course-create'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/edit/<slug:slug>/', views.CourseUpdateView.as_view(), name='course-update'),
]

