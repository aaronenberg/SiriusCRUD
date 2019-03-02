from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


STUDENT = 'ST'
TEACHING_ASSISTANT = 'TA'
FACULTY = 'FA'
ACCOUNT_TYPES = (
    (STUDENT, 'Student'),
    (TEACHING_ASSISTANT, 'Teaching Assistant'),
    (FACULTY, 'Faculty'),
)


class BaseUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email,  password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('account_type', STUDENT)
        return self._create_user(email, password)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_type', FACULTY)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('account_type') is not FACULTY:
            raise ValueError('Superuser must have account type="FA"')
        return self._create_user(email, password, **extra_fields)


class BaseUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='School Email',
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    account_type = models.CharField(
        max_length=2,
        default=STUDENT,
        choices=ACCOUNT_TYPES,
        verbose_name='Account Type'
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

    objects = BaseUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = USERNAME_FIELD

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    @property
    def is_privileged(self):
        return self.is_staff or self.account_type in [TEACHING_ASSISTANT, FACULTY]

    class Meta:
        verbose_name_plural = "Users"

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

