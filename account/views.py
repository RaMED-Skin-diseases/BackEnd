from django.utils import timezone
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.serializers import serialize
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken, AccessToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
import os


def generate_verification_code(length=6):
    """Generate a random verification code of given length."""
    return ''.join(random.choices(string.digits, k=length))


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['user_type'] = user.user_type
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def email_code(user):
    subject = 'Verification Code'
    message = (
        f"Hi Dr. {user.f_name} {user.l_name},\n\n"
        f"Use the following code to verify your email address:\n\n"
        f"{user.verification_code}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"Regards,\nSkinWise Team"
    ) if user.user_type == "Doctor" else (
        f"Hi {user.f_name} {user.l_name},\n\n"
        f"Use the following code to verify your email address:\n\n"
        f"{user.verification_code}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"Regards,\nSkinWise Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
              [user.email], fail_silently=False)


@csrf_exempt
def signup(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        date_of_birth = request.POST.get("date_of_birth")
        email = request.POST.get("email").lower()
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username").lower()
        user_type = request.POST.get("user_type")
        info = request.POST.get("info")
        specialization = request.POST.get("specialization")
        clinic_details = request.POST.get("clinic_details")

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        try:
            MinLengthValidator(8)(password)
        except ValidationError:
            return JsonResponse({'error': 'Password must be at least 8 characters long.'}, status=400)
        try:
            MinLengthValidator(3)(username)
            RegexValidator(r'^(?=.*[a-zA-Z])[a-zA-Z0-9._-]*$',
                           message="Username must include at least one letter and can only contain '.', '_', or '-'")(username)
        except ValidationError:
            return JsonResponse({'error': 'Username must be at least 3 characters long and include letters.'}, status=400)
        try:
            RegexValidator(r'^[a-zA-Z]+$')(f_name)
        except ValidationError:
            return JsonResponse({'error': 'First name must contain only letters.'}, status=400)
        try:
            RegexValidator(r'^[a-zA-Z]+$')(l_name)
        except ValidationError:
            return JsonResponse({'error': 'Last name must contain only letters.'}, status=400)

        # Handle doctor verification image
        verification_image = None
        if user_type == "Doctor":
            if 'verification_image' not in request.FILES:
                return JsonResponse({'error': 'Doctor verification document is required'}, status=400)

            verification_image = request.FILES['verification_image']
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if verification_image.content_type not in allowed_types:
                return JsonResponse({'error': 'Only JPEG, PNG, or PDF files are allowed'}, status=400)

            # Validate file size (max 5MB)
            if verification_image.size > 5 * 1024 * 1024:
                return JsonResponse({'error': 'File size must be less than 5MB'}, status=400)

        user = User(
            f_name=f_name,
            l_name=l_name,
            date_of_birth=date_of_birth,
            email=email,
            gender=gender,
            password=make_password(password),
            username=username,
            user_type='Patient',
            original_user_type=user_type,
            info=info,
            specialization=specialization,
            clinic_details=clinic_details,
            is_verified=False,
            verification_status='pending' if user_type == 'Doctor' else 'approved'
        )

        if user_type == 'Doctor':
            user.verification_image = request.FILES['verification_image']

        user.save()

        try:
            user.save()  # Save user first
            send_verification_code(user.username)  # Then send email

            return JsonResponse({
                'message': 'User registered successfully. Please check your email for the verification code.',
            }, status=200)

        except Exception as e:
            # Only delete if user was saved
            if user.pk:
                user.delete()

            # Check if it's an email error specifically
            if "email" in str(e).lower():
                return JsonResponse({
                    'error': 'Failed to send verification email. Please try again later.',
                    'debug': str(e)  # Remove in production
                }, status=400)
            else:
                return JsonResponse({
                    'error': 'Registration failed. Please try again.',
                    'debug': str(e)  # Remove in production
                }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_profile(request, username):
    user = User.objects.filter(username=username).first()

    if user:
        profile_data = {
            'f_name': user.f_name,
            'l_name': user.l_name,
            'date_of_birth': user.date_of_birth,
            'gender': user.gender,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'info': user.info,
            'specialization': user.specialization,
            'clinic_details': user.clinic_details,
            'verification_status': user.verification_status if user.user_type == 'Doctor' else None
        }
        return JsonResponse({'user': profile_data}, status=200)
    else:
        return JsonResponse({'error': 'User not found.'}, status=404)


@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        email_username = request.POST.get("email")
        code = request.POST.get("verification_code")
        expiry_time = timezone.timedelta(minutes=10)
        user = User.objects.filter(email=email_username, verification_code=code).first() or \
            User.objects.filter(username=email_username,
                                verification_code=code).first()
        if user:
            if user.code_created_at and timezone.now() - user.code_created_at < expiry_time:
                user.is_verified = True
                user.verification_code = None
                user.code_created_at = None
                user.save()
                return JsonResponse({'message': 'Email verified successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid verification code or code has expired.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid verification code or email.'}, status=400)
    return render(request, "account/verify_email.html")


def resend_verification_code(request, username):
    if request.method == "GET":
        username = username.lower()
        if not User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User not found.'}, status=404)
        try:
            send_verification_code(username)
            return JsonResponse({'message': 'Verification code sent. Please check your email.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Failed to send email. Please try again later.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def send_verification_code(username):
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': 'User not found.'}, status=404)
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.code_created_at = timezone.now()
        user.save()
        email_code(user)
        return JsonResponse({'message': 'Verification code sent. Please check your email.'}, status=200)
    except Exception as e:
        return str(e)


@api_view(['POST'])
def login(request):
    username_email = request.data.get("username_email", "").strip().lower()
    password = request.data.get("password")

    if not username_email or not password:
        return JsonResponse({'error': 'Username/email and password are required.'}, status=400)

    user = User.objects.filter(username=username_email).first() or \
        User.objects.filter(email=username_email).first()

    if user is None:
        return JsonResponse({'error': 'Invalid username or email.'}, status=400)

    if not user.is_verified:
        return JsonResponse({'error': 'Email not verified. Please verify your email.'}, status=403)

    if user.check_password(password):
        token = CustomTokenObtainPairSerializer.get_token(user)
        return JsonResponse({
            'access': str(token.access_token),
            'refresh': str(token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
            }
        }, safe=False, status=status.HTTP_200_OK)

    return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
def forgot_password(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        print(username_email)
        try:
            user = User.objects.filter(email=username_email).first() or User.objects.filter(
                username=username_email).first()
            send_verification_code(user.username)
            return JsonResponse({'message': 'Verification code sent. Please check your email.'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or username.'}, status=400)
    return render(request, "account/forgot_password.html")


@csrf_exempt
def verify_reset_code(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        code = request.POST.get("verification_code")
        expiry_time = timezone.timedelta(minutes=10)
        try:
            user = User.objects.filter(email=username_email, verification_code=code).first() or \
                User.objects.filter(username=username_email,
                                    verification_code=code).first()
            if user.code_created_at and timezone.now() - user.code_created_at < expiry_time:
                # Store the username/email in the session for the next step
                request.session['reset_user'] = user.username
                return JsonResponse({'message': 'Email verified successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid verification code or code has expired.'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid verification code or email.'}, status=400)
    return render(request, "account/verify_reset_code.html")


@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        username = request.session.get('reset_user')
        if not username:
            return JsonResponse({'error': 'Session expired or invalid request.'}, status=400)

        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': 'User not found.'}, status=404)

        # Validate the new password
        try:
            MinLengthValidator(8)(new_password)
        except ValidationError:
            return JsonResponse({'error': 'Password must be at least 8 characters long.'}, status=400)

        # Save the new password and clear reset code
        user.password = make_password(new_password)
        user.verification_code = None
        user.code_created_at = None
        user.save()

        # Clear the session
        del request.session['reset_user']

        return JsonResponse({'message': 'Password reset successfully.'}, status=200)
    return render(request, "account/reset_password.html")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_profile(request, username):
    user = User.objects.filter(username=username).first()

    if user:
        profile_data = {
            'f_name': user.f_name,
            'l_name': user.l_name,
            'date_of_birth': user.date_of_birth,
            'gender': user.gender,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'info': user.info,
            'specialization': user.specialization,
            'clinic_details': user.clinic_details,
            'verification_status': user.verification_status if user.user_type == 'Doctor' else None
        }
        return JsonResponse({'user': profile_data}, status=200)
    else:
        return JsonResponse({'error': 'User not found.'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        access_token = request.data.get("access")

        if not refresh_token or not access_token:
            return JsonResponse({"error": "Both access and refresh tokens are required"}, status=400)

        # Blacklist the Refresh Token
        refresh = RefreshToken(refresh_token)
        refresh.blacklist()

        # Blacklist the Access Token
        access = AccessToken(access_token)

        # Check if the access token already exists in OutstandingToken
        outstanding_token, created = OutstandingToken.objects.get_or_create(
            jti=access["jti"],
            defaults={"token": str(
                access), "user": request.user, "expires_at": now()}
        )

        # Blacklist the access token only if it was newly created
        BlacklistedToken.objects.get_or_create(token=outstanding_token)

        return JsonResponse({"message": "Successfully logged out"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    user = request.user
    data = request.data

    # Update fields only if they are provided
    if "f_name" in data:
        f_name = data.get("f_name")
        try:
            RegexValidator(r'^[a-zA-Z]+$')(f_name)
        except ValidationError:
            return JsonResponse({'error': 'First name must contain only letters.'}, status=400)
        user.f_name = f_name

    if "l_name" in data:
        l_name = data.get("l_name")
        try:
            RegexValidator(r'^[a-zA-Z]+$')(l_name)
        except ValidationError:
            return JsonResponse({'error': 'Last name must contain only letters.'}, status=400)
        user.l_name = l_name

    if "date_of_birth" in data:
        user.date_of_birth = data.get("date_of_birth")

    if "gender" in data:
        user.gender = data.get("gender")

    if "email" in data:
        email = data.get("email")
        if User.objects.filter(email=email).exists() and user.email != email:
            return JsonResponse({'error': 'Email already exists'}, status=400)
        old_email = user.email
        user.email = email

    if "username" in data:
        username = data.get("username")
        if User.objects.filter(username=username).exists() and user.username != username:
            return JsonResponse({'error': 'Username already exists'}, status=400)
        user.username = username

    # If user is a doctor, allow updating additional fields
    if user.user_type == "Doctor":
        if "info" in data:
            user.info = data.get("info")
        if "specialization" in data:
            user.specialization = data.get("specialization")
        if "clinic_details" in data:
            user.clinic_details = data.get("clinic_details")

        # Handle new verification image upload if provided
    if 'verification_image' in request.FILES:
        verification_image = request.FILES['verification_image']
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if verification_image.content_type not in allowed_types:
            return JsonResponse({'error': 'Only JPEG, PNG, or PDF files are allowed'}, status=400)
        if verification_image.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'File size must be less than 5MB'}, status=400)

        # Delete old image if exists
        if user.verification_image:
            user.verification_image.delete()

        user.verification_image = verification_image
        # Reset verification status when a new document is uploaded
        user.verification_status = 'pending'

    user.save()

    # If email changed, reset verification
    if "email" in data and old_email != email:
        user.is_verified = False
        user.verification_code = None
        user.code_created_at = None
        user.save()
        send_verification_code(user.username)
        return JsonResponse({'message': 'Verification code sent successfully.'}, status=200)

    return JsonResponse({'message': 'Profile updated successfully.'}, status=200)
