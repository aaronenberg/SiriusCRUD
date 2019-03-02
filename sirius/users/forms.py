from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.forms import ValidationError, EmailField
from .models import BaseUser


class UserCreateForm(ModelForm):
   
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name",)
        field_classes = {'email': EmailField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def clean_email(self):
        whitelist = ['edu']
        email = self.cleaned_data['email']
        top_level_domain = email.rsplit('.').pop()
        if top_level_domain not in whitelist:
            raise ValidationError("Email must be a valid school email that ends with .edu")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.set_unusable_password()
        if commit:
            user.save()
        return user
