from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=225, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    # required fields? for superuser?
    REQUIRED_FIELDS = ['phone_number', 'email', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
