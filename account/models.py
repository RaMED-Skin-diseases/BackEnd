from django.db import models

# Create your models here.


class Signup_patient(models.Model):
    f_name = models.CharField(max_length=100)
    l_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=6)
    password = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)


class Signup_doc(models.Model):
    f_name = models.CharField(max_length=100)
    l_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=6)
    password = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    info = models.TextField()
    specialization = models.CharField(max_length=100)
    clinic_details = models.TextField()
