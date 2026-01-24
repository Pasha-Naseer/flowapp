from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.utils import timezone
from django.db.models.signals import post_save


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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default='fallback.png')
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    bio = models.TextField()

    def __str__(self):
        return f"{self.user}"


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance, first_name=instance.first_name, last_name=instance.last_name)
        user_profile.save()


post_save.connect(create_profile, sender=User)


class OtpCode(models.Model):
    phone_number = models.CharField(max_length=12)
    code = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phone_number} - {self.code} - {self.created.time()} - {timezone.localtime(self.created).date()}'

    def calculate_time(self):
        create_time = timezone.localtime(self.created).time()
        return create_time

    def calculate_date(self):
        create_date = timezone.localtime(self.created).date()
        return create_date

