from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


STUDENT = 'ST'
TEACHING_ASSISTANT = 'TA'
FACULTY = 'FA'
ACCOUNT_TYPES = (
    (STUDENT, 'Student'),
    (TEACHING_ASSISTANT, 'Teaching Assistant'),
    (FACULTY, 'Faculty'),
)


class BaseUserManager(BaseUserManager):

    def _create_user(self, email, password, account_type, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        if not account_type:
            raise ValueError('Account type is required.')
        user = self.model(email=self.normalize_email(email), account_type=account_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email,  password, account_type, **extra_fields):
        user = self._create_user(email, account_type, password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, account_type, **extra_fields):
        user = self._create_user(email, password, account_type)
        user.is_staff = True
        user.save(using=self._db)
        return user


class BaseUser(AbstractBaseUser):

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='CSUS Email',
    )
    account_type = models.CharField(
        max_length=2,
        default=STUDENT,
        choices=ACCOUNT_TYPES,
        verbose_name='Account Type'
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='First Name'
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Last Name'
    )
    middle_initial = models.CharField(
        max_length=1,
        blank=True,
        verbose_name='MI'
    )
    date_joined = models.DateField(
        auto_now_add=True,
        verbose_name='Date Joined'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = USERNAME_FIELD
    REQUIRED_FIELDS = ['account_type', ]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_privileged(self):
        return self.is_staff or self.account_type in [TEACHING_ASSISTANT, FACULTY]

    class Meta:
        verbose_name_plural = "Users"

