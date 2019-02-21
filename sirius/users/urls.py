from django.urls import path
from .views import SignUpView


urlpatterns = [
        path('auth/login/', SignUpView.as_view(), name="SignUp")
]
