from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import path
from .views import UserCreateView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
]
