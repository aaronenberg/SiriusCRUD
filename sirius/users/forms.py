from django.contrib.auth import forms as auth_forms
from django.forms import (
    CharField,
    ValidationError,
    EmailField,
    ModelForm,
    TextInput,
    ChoiceField,
    Select,
    SelectMultiple,
    HiddenInput,
    ModelMultipleChoiceField,
    PasswordInput
)
from django.utils.translation import gettext_lazy as _
from .models import BaseUser, USER_TYPE_CHOICES
from courses.models import Course


class UserCreateForm(ModelForm):
   
    class Meta:
        model = BaseUser
        fields = ("username", "email", "first_name", "last_name",)
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


class AccountUpdateFormPrivileged(ModelForm):
   
    user_type = ChoiceField(choices=USER_TYPE_CHOICES,
        widget = Select(attrs={
            'id': 'user-user-type',
            'class': 'form-control custom-select select-fix-height',
            'name': 'user-type',
        }),
    )
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name", "user_type", "username")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = TextInput(attrs={
            'id': 'user-email',
            'class': 'form-control',
            'name': 'email',
        })
        self.fields['first_name'].widget = TextInput(attrs={
            'id': 'user-first-name',
            'class': 'form-control',
            'name': 'first-name',
        })
        self.fields['last_name'].widget = TextInput(attrs={
            'id': 'user-last-name',
            'class': 'form-control',
            'name': 'last-name',
        })
        self.fields['username'].widget = TextInput(attrs={
            'id': 'user-username',
            'class': 'form-control',
            'name': 'username',
            'autocomplete': 'new-password',
        })
        self.fields['email'].disabled = True
        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True
        self.fields['username'].disabled = True


class AccountUpdateForm(ModelForm):
   
    user_type = ChoiceField(choices=USER_TYPE_CHOICES,
        widget = Select(attrs={
            'id': 'user-user-type',
            'class': 'form-control custom-select select-fix-height',
            'name': 'user-type',
        }),
    )
    courses = ModelMultipleChoiceField(queryset=Course.objects.all(),
        widget = SelectMultiple(attrs={
            'id': 'sirius-courses',
            'class': 'custom-select form-control',
            'name': 'courses',
        }),
        required=False,
    )
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name", "user_type", "username", "courses")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.user_type != 'FA':
            self.fields['user_type'].disabled = True
            self.fields['user_type'].widget = HiddenInput()
        self.fields['username'].disabled = True
        self.fields['email'].widget = TextInput(attrs={
            'id': 'user-email',
            'class': 'form-control',
            'name': 'email',
        })
        self.fields['first_name'].widget = TextInput(attrs={
            'id': 'user-first-name',
            'class': 'form-control',
            'name': 'first-name',
        })
        self.fields['last_name'].widget = TextInput(attrs={
            'id': 'user-last-name',
            'class': 'form-control',
            'name': 'last-name',
        })
        self.fields['username'].widget = TextInput(attrs={
            'id': 'user-username',
            'class': 'form-control',
            'name': 'username',
        })

    def clean_email(self):
        whitelist = ['edu']
        email = self.cleaned_data['email']
        top_level_domain = email.rsplit('.').pop()
        if top_level_domain not in whitelist:
            raise ValidationError("Email must be a valid school email that ends with .edu")
        return email


class PasswordChangeForm(auth_forms.PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class AuthenticationForm(auth_forms.AuthenticationForm):

    username = auth_forms.UsernameField(widget=TextInput(attrs={
        'autofocus': True,
        'placeholder': 'Username/Email',
        })
    )
    password = CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={
            'placeholder': 'Password',
        }),
    )

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
