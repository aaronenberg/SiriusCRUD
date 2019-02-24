from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import BaseUser


class UserCreateForm(UserCreationForm):
   
    class Meta:
        model = BaseUser
        fields = ("email",)
        field_classes = {'email': UsernameField}

