from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import path
from .views import UserCreateView, UserActivateView


app_name = 'users'

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('activate/', UserActivateView.as_view(), name='activate'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
]
