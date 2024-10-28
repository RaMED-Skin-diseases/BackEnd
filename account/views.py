from django.utils import timezone
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, TempUser
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime


# Create your views here.

def generate_verification_code(length=6):
    """Generate a random verification code of given length."""
    return ''.join(random.choices(string.digits, k=length))


@csrf_exempt
def signup(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        date_of_birth = request.POST.get("date_of_birth")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username")
        user_type = request.POST.get("user_type")
        info = request.POST.get("info")
        specialization = request.POST.get("specialization")
        clinic_details = request.POST.get("clinic_details")
        verification_code = generate_verification_code()

        if User.objects.filter(email=email).exists() or TempUser.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")
        if User.objects.filter(username=username).exists() or TempUser.objects.all().filter(username=username).exists():
            return HttpResponse("Username already exits.")

        temp_user = TempUser(
            f_name=f_name,
            l_name=l_name,
            date_of_birth=date_of_birth,
            email=email,
            gender=gender,
            password=password,
            username=username,
            user_type=user_type,
            info=info,
            specialization=specialization,
            clinic_details=clinic_details,
            verification_code=verification_code,
            code_created_at=timezone.now(),
        )
        temp_user.save()

        try:
            if user_type == "Patient":
                send_mail(
                    'Verification Code',
                    f'Hi {f_name} {l_name},\n\nUse the following code to verify your email address to complete your signup process:\n\n {
                        verification_code} \n\nThis code will expire in 10 minutes.\n\nRegards,\nRaMed Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            else:
                send_mail(
                    'Verification Code',
                    f'Hi DR. {f_name} {l_name},\n\nUse the following code to verify your email address to complete your signup process:\n\n {
                        verification_code} \n\nThis code will expire in 10 minutes.\n\nRegards,\nRaMed Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            return HttpResponse("User registered successfully. Please check your email for the verification code.")
        except Exception as e:
            temp_user.delete()
            return HttpResponse("Failed to send email. Please try again later.")
    return render(request, "account/signup.html")


@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("verification_code")
        expiry_time = timezone.timedelta(minutes=10)

        temp_user = TempUser.objects.get(
            email=email, verification_code=code)

        try:
            if timezone.now() - temp_user.code_created_at < expiry_time:
                user = User(
                    f_name=temp_user.f_name,
                    l_name=temp_user.l_name,
                    date_of_birth=temp_user.date_of_birth,
                    email=temp_user.email,
                    gender=temp_user.gender,
                    password=temp_user.password,
                    username=temp_user.username,
                    user_type=temp_user.user_type,
                    info=temp_user.info,
                    specialization=temp_user.specialization,
                    clinic_details=temp_user.clinic_details,
                    is_verified=True,
                )
                user.save()

                temp_user.delete()
                return HttpResponse("Email verified successfully. You are now registered.")
            else:
                temp_user.delete()
                return HttpResponse("Verification code has expired.")
        except TempUser.DoesNotExist:
            if timezone.now() - temp_user.code_created_at < expiry_time:
                temp_user.delete()
            return HttpResponse("Invalid verification code.")
    return render(request, "account/verify_email.html")


@csrf_exempt
def login(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email")
        password = request.POST.get("password")

        user = User.objects.filter(username=username_email).first(
        ) or User.objects.filter(email=username_email).first()

        if user.is_verified:
            if user and user.password == password:
                return HttpResponse("Login successful.")
            else:
                return HttpResponse("Invalid credentials.")
        else:
            return HttpResponse("Email not verified. Please verify your email to login.")

    return render(request, "account/login.html")
