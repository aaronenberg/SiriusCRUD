from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError, EmailField, ModelForm, TextInput, ChoiceField, Select
from .models import BaseUser, USER_TYPE_CHOICES


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
            'id': 'user_user_type',
            'class': 'form-control custom-select select-fix-height',
            'name': 'user_type',
        }),
    )
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name", "user_type",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = TextInput(attrs={
            'id': 'user_email',
            'class': 'form-control',
            'name': 'email',
        })
        self.fields['first_name'].widget = TextInput(attrs={
            'id': 'user_first_name',
            'class': 'form-control',
            'name': 'first_name',
        })
        self.fields['last_name'].widget = TextInput(attrs={
            'id': 'user_last_name',
            'class': 'form-control',
            'name': 'last_name',
        })
        self.fields['email'].disabled = True
        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True


class AccountUpdateForm(ModelForm):
   
    user_type = ChoiceField(choices=USER_TYPE_CHOICES,
        widget = Select(attrs={
            'id': 'user_user_type',
            'class': 'form-control custom-select select-fix-height',
            'name': 'user_type',
        }),
    )
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name", "user_type",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.user_type != 'FA':
            self.fields['user_type'].disabled = True
        self.fields['email'].widget = TextInput(attrs={
            'id': 'user_email',
            'class': 'form-control',
            'name': 'email',
            'autocomplete': 'new-password',
        })
        self.fields['first_name'].widget = TextInput(attrs={
            'id': 'user_first_name',
            'class': 'form-control',
            'name': 'first_name',
            'autocomplete': 'new-password',
        })
        self.fields['last_name'].widget = TextInput(attrs={
            'id': 'user_last_name',
            'class': 'form-control',
            'name': 'last_name',
            'autocomplete': 'new-password',
        })

    def clean_email(self):
        whitelist = ['edu']
        email = self.cleaned_data['email']
        top_level_domain = email.rsplit('.').pop()
        if top_level_domain not in whitelist:
            raise ValidationError("Email must be a valid school email that ends with .edu")
        return email

