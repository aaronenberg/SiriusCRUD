from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('activate/', views.UserActivateView.as_view(), name='activate'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('user/<pk>', views.UserDetailView.as_view(), name='user-detail'),
    path('account/', views.AccountDetailView.as_view(), name='account-detail'),
    path('account-edit/', views.AccountUpdateView.as_view(), name='account-update'),
    path('user/set-account-type/<pk>', views.AccountTypeUpdateView.as_view(), name='account-type-update'),
]
