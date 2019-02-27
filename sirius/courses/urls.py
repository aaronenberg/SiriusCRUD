from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/new/', views.CourseCreateView.as_view(), name='course-create'),
    path('courses/<slug:slug>/', views.CourseDetailSectionListView.as_view(), name='course-detail-section-list'),
    path('courses/<str:subject>/', views.CourseSubjectListView.as_view(), name='course-subject-list'),
    #path('courses/<slug:slug>/<int:section>/', views.SectionArticleListView.as_view(), name='section-article-list'),
]

