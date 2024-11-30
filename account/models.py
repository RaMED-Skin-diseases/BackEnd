from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator


# Create your models here.


GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

USER_TYPE_CHOICES = [
    ('Patient', 'Patient'),
    ('Doctor', 'Doctor'),
]

username_validator = RegexValidator(
    r'^(?=.*[a-zA-Z])[a-zA-Z0-9]*$',
    'Username must contain at least one letter and can include numbers and special characters.'
)

name_validator = RegexValidator(
    r'^[a-zA-Z]+$', 'name must contain only letters.')


class User(models.Model):
    f_name = models.CharField(
        max_length=100, blank=False, null=False, validators=[name_validator])
    l_name = models.CharField(
        max_length=100, blank=False, null=False, validators=[name_validator])
    date_of_birth = models.DateField(null=False, blank=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, blank=False, null=False)
    password = models.CharField(
        max_length=20, blank=False, null=False, validators=[MinLengthValidator(8)])
    username = models.CharField(
        max_length=20, unique=True, blank=False, null=False, validators=[username_validator, MinLengthValidator(3)])

    user_type = models.CharField(
        max_length=7, choices=USER_TYPE_CHOICES, blank=False, null=False)

    info = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100, null=True)
    clinic_details = models.TextField(blank=True, null=True)

    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"