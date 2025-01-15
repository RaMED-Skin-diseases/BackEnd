from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.management.base import BaseCommand
from django.utils import timezone




# Create your models here.
# class AdminUserManager(BaseUserManager):
#     def create_superuser(self, username, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(username, password, **extra_fields)

#     def create_user(self, username, password=None, **extra_fields):
#         if not username:
#             raise ValueError('The Username field must be set')

#         user = self.model(username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
class AdminUserManager(BaseUserManager):
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('date_of_birth', timezone.now().date())  # Default date

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
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


# class AdminUser(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(max_length=50, unique=True)
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)

#     # Add custom related names
#     groups = models.ManyToManyField(
#         'auth.Group',
#         verbose_name='admin groups',
#         blank=True,
#         help_text='The groups this admin belongs to.',
#         related_name='admin_user_set',
#         related_query_name='admin_user'
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         verbose_name='admin user permissions',
#         blank=True,
#         help_text='Specific permissions for this admin user.',
#         related_name='admin_user_set',
#         related_query_name='admin_user'
#     )

#     objects = AdminUserManager()

#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = []

#     def __str__(self):
#         return self.username

#     class Meta:
#         verbose_name = 'Admin User'
#         verbose_name_plural = 'Admin Users'


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
        max_length=20, blank=False, null=False, validators=[MinLengthValidator(8)])
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

    info = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100, null=True)
    clinic_details = models.TextField(blank=True, null=True)

    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    objects = AdminUserManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"

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
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

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
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))