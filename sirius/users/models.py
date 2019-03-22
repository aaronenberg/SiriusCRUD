import re
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from courses.models import Course


STUDENT = 'ST'
TEACHING_ASSISTANT = 'TA'
FACULTY = 'FA'
USER_TYPE_CHOICES = (
    (STUDENT, 'Student'),
    (TEACHING_ASSISTANT, 'Teaching Assistant'),
    (FACULTY, 'Instructor'),
)


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        if not username:
            raise ValueError('Username is required.')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email,  password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('user_type', STUDENT)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', FACULTY)
        extra_fields.setdefault('first_name', 'superuser')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('user_type') is not FACULTY:
            raise ValueError('Superuser must have user type="FA"')
        return self._create_user(username, email, password, **extra_fields)


class AlphaNumericUsernameValidator(RegexValidator):
    regex = r'^_?[a-zA-Z]+?[\w]*$'
    message = _(
        'Username must be 30 characters or fewer, must start with either a letter or '
        'underscore followed by a letter, and may contain a combination of letters, numbers and underscore.'
    )
    flags = re.ASCII


class BaseUser(AbstractBaseUser, PermissionsMixin):

    username_validator = AlphaNumericUsernameValidator()

    username = models.CharField(
        max_length=30,
        primary_key=True,
        help_text=_('Required. 30 characters or fewer. Letters and digits only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("That username is already taken."),
        },
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='School Email',
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    user_type = models.CharField(
        max_length=2,
        default=STUDENT,
        choices=USER_TYPE_CHOICES,
        verbose_name='User Type'
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='First Name'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Last Name'
    )
    courses = models.ManyToManyField(Course, related_name='courses')

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        if all((self.first_name, self.last_name)) and not all((self.first_name.isspace(), self.last_name.isspace())):
            return "{0} {1}".format(self.first_name, self.last_name)
        return self.username

    def get_short_name(self):
        if self.first_name and not self.first_name.isspace():
            return self.first_name
        return self.username

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:user-detail", kwargs={"pk": self.pk})

    @property
    def is_privileged(self):
        return self.is_staff or self.user_type in [TEACHING_ASSISTANT, FACULTY]

    class Meta:
        verbose_name_plural = "Users"

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

