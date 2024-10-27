from django.db import models

# Create your models here.


GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

USER_TYPE_CHOICES = [
    ('Patient', 'Patient'),
    ('Doctor', 'Doctor'),
]


class User(models.Model):
    f_name = models.CharField(max_length=100)
    l_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    password = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    info = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100, null=True)
    clinic_details = models.TextField(blank=True, null=True)

    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
