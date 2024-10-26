from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.


GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]


class Signup_patient(models.Model):
    f_name = models.CharField(max_length=100)
    l_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    password = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Signup_doc(models.Model):
    f_name = models.CharField(max_length=100)
    l_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    password = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    info = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100)
    clinic_details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)
