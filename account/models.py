from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.management.base import BaseCommand
from django.utils import timezone
import os
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

# Create your models here.
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

USER_TYPE_CHOICES = [
    ('Patient', 'Patient'),
    ('Doctor', 'Doctor'),
]

username_validator = RegexValidator(r'^(?=.*[a-zA-Z])[a-zA-Z0-9._-]*$',
                                    "Username must include at least one letter and can only contain '.', '_', or '-'"
                                    )

name_validator = RegexValidator(
    r'^[a-zA-Z]+$', 'name must contain only letters.')


class DoctorVerificationStorage(S3Boto3Storage):
    location = 'doctor-verifications'
    file_overwrite = False
    default_acl = 'private'


class AdminUserManager(BaseUserManager):
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.pop('date_of_birth', None)  # Remove unnecessary field

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')

        extra_fields.setdefault('date_of_birth', timezone.now().date())
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


def doctor_verification_upload_path(instance, filename):
    # This will create paths like: doctor_verifications/username/filename
    return os.path.join('doctor_verifications', instance.username, filename)


class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='user groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    f_name = models.CharField(
        max_length=100, blank=False, null=False, validators=[name_validator])
    l_name = models.CharField(
        max_length=100, blank=False, null=False, validators=[name_validator])
    date_of_birth = models.DateField(null=False, blank=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, blank=False, null=False)
    password = models.CharField(
        max_length=128, blank=False, null=False, validators=[MinLengthValidator(8)])
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    user_type = models.CharField(
        max_length=7, choices=USER_TYPE_CHOICES, blank=False, null=False)

    original_user_type = models.CharField(
        max_length=7,
        choices=USER_TYPE_CHOICES,
        blank=True,
        null=True
    )

    info = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100, null=True)
    clinic_details = models.TextField(blank=True, null=True)

    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    verification_image = models.ImageField(
        upload_to='doctor-verifications/',
        storage=DoctorVerificationStorage(),  # Explicitly use our storage class
        blank=True,
        null=True,
        verbose_name="Doctor Verification Document",
        help_text="Upload your medical license or ID for verification"
    )
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    verification_notes = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_users")

    objects = AdminUserManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()

        # Ensure correct default verification status
        if not self.pk:  # Only for new users
            if self.user_type == 'Doctor':
                self.verification_status = 'pending'
                self.user_type = 'Patient'  # Start as Patient until approval
            else:
                self.verification_status = 'patient'

        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"

    @property
    def requires_verification(self):
        return self.user_type == 'Doctor' and not self.is_verified


class AdminUser(User):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new instances
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)


class Command(BaseCommand):
    help = 'Creates a superuser with the specified credentials'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str,
                            help='Username for the superuser')
        parser.add_argument('--email', type=str,
                            help='Email for the superuser')
        parser.add_argument('--password', type=str,
                            help='Password for the superuser')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')

        if not all([username, email, password]):
            # Interactive mode
            username = input('Username: ')
            email = input('Email: ')
            password = input('Password: ')

        try:
            admin_user = AdminUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superuser {username} created successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error creating superuser: {str(e)}'))
