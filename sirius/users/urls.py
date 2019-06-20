from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views


app_name = 'users'


urlpatterns = [
    path('register', views.UserCreateView.as_view(), name='register'),
    path('login', views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('activate', views.UserActivateView.as_view(), name='activate'),
    path('account/password-change',
         views.PasswordChangeView.as_view(success_url=reverse_lazy('users:password_change_done')),
         name="password_change"),
    path('account/password-change/success', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path('password-reset',
         views.PasswordResetView.as_view(success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),
    path('password-reset/sent', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>',
         views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/success', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('users', views.UserListView.as_view(), name='user-list'),
    path('users/<pk>', views.UserUpdateView.as_view(), name='user-detail'),
    path('users/search/results', views.UserSearchResultsView.as_view(), name='user-search-results'),
    path('account', views.AccountUpdateView.as_view(), name='account-update'),
]


