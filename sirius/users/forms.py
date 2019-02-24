from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.core.validators import EmailValidator
from django.forms import ValidationError
from .models import BaseUser


class UserCreateForm(UserCreationForm):
   
    class Meta:
        model = BaseUser
        fields = ("email",)
        field_classes = {'email': UsernameField}

    def clean_email(self):
        whitelist = ['csus.edu']
        email = self.cleaned_data['email']
        user_part, domain_part = email.rsplit('@', 1)
        if domain_part not in whitelist:
            raise ValidationError("Email must be a valid school email that ends with .edu")
        return email
