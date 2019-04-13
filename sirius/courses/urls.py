from django.urls import path
from . import views


app_name = 'courses'

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='subject-list'),
    path('<str:subject>/', views.SubjectCoursesListView.as_view(), name='subject-courses-list'),
    path('create/new/', views.CourseCreateView.as_view(), name='course-create'),
    path('<str:subject>/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<str:subject>/<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),
    path('<str:subject>/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course-update'),
]

