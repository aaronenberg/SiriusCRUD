from django.contrib.auth import (
    forms as auth_forms,
    password_validation
)
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
from .models import BaseUser, StaffProfile, USER_TYPE_CHOICES
from courses.models import Course


class UserCreateForm(ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = CharField(label=_("Password"),
        widget=PasswordInput
    )
    password2 = CharField(label=_("Confirm Password"),
        widget=PasswordInput,
        help_text=_("Enter the same password as above, for verification.")
    )

    class Meta:
        model = BaseUser
        fields = ("username", "email",)
        field_classes = {'email': EmailField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.EMAIL_FIELD].widget.attrs.update({'autofocus': True})
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        whitelist = ['edu']
        email = self.cleaned_data['email']
        top_level_domain = email.rsplit('.').pop()
        if top_level_domain not in whitelist:
            raise ValidationError("Please enter a valid school email that ends with .edu")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super(UserCreateForm, self)._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        if commit:
            user.save()
        return user


class AccountUpdateFormPrivileged(ModelForm):
   
    user_role = ChoiceField(choices=USER_TYPE_CHOICES,
        widget = Select(attrs={
            'id': 'user-user-type',
            'class': 'form-control custom-select select-fix-height',
            'name': 'user-type',
        }),
    )
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name", "user_role", "username", "is_active")

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

    def clean_is_active(self):
        return self.instance.is_active


class AccountUpdateForm(ModelForm):
   
    user_role = ChoiceField(choices=USER_TYPE_CHOICES,
        widget = Select(attrs={
            'id': 'user-user-type',
            'class': 'form-control custom-select select-fix-height',
            'name': 'user-type',
        }),
    )
    class Meta:
        model = BaseUser
        fields = ("email", "first_name", "last_name", "user_role", "username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.user_role != 'FA':
            self.fields['user_role'].disabled = True
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

    def clean_is_active(self):
        return self.instance.is_active


class StaffProfileForm(ModelForm):

    class Meta:
        model = StaffProfile
        fields = ("courses",)

    courses = ModelMultipleChoiceField(queryset=Course.objects.extra(
        select={'course_number': "CAST(substring(number FROM '^[0-9]+') AS INTEGER)"}
        ).order_by('subject','course_number'),
        widget = SelectMultiple(attrs={
            'id': 'sirius-courses',
            'class': 'custom-select form-control',
            'name': 'courses',
        }),
        required=False,
    )

class PasswordChangeForm(auth_forms.PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class PasswordResetForm(auth_forms.PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class SetPasswordForm(auth_forms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
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
