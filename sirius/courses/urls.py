from django.urls import path
from . import views


app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('create/new/', views.CourseCreateView.as_view(), name='course-create'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course-update'),
]

