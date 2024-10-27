from django.utils import timezone
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
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

        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exits.")

        request.session['user_data'] = {
            'f_name': f_name,
            'l_name': l_name,
            'date_of_birth': date_of_birth,
            'email': email,
            'gender': gender,
            'password': password,
            'username': username,
            'user_type': user_type,
            'info': info,
            'specialization': specialization,
            'clinic_details': clinic_details,
            'verification_code': verification_code,
            'verification_code': verification_code,
            'code_created_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        send_mail(
            'Verify Your Email',
            f'Your verification code is: {verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return HttpResponse("User registered successfully. Please check your email for the verification code.")
    return render(request, "account/signup.html")


@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("verification_code")
        user_data = request.session.get('user_data')

        if user_data:
            if 'email' in user_data and user_data['email'] == email:
                if user_data['verification_code'] == code:
                    code_created_at = datetime.strptime(
                        user_data['code_created_at'], '%Y-%m-%d %H:%M:%S')
                    code_created_at = timezone.make_aware(code_created_at)
                    if timezone.now() - code_created_at < timezone.timedelta(minutes=5):
                        user = User(
                            f_name=user_data['f_name'],
                            l_name=user_data['l_name'],
                            date_of_birth=user_data['date_of_birth'],
                            email=user_data['email'],
                            gender=user_data['gender'],
                            password=user_data['password'],
                            username=user_data['username'],
                            user_type=user_data['user_type'],
                            info=user_data['info'],
                            specialization=user_data['specialization'],
                            clinic_details=user_data['clinic_details'],
                            is_verified=True,
                        )
                        user.save()
                        del request.session['user_data']
                        return HttpResponse("Email verified successfully. You are now registered.")
                    else:
                        return HttpResponse("Verification code has expired.")
                else:
                    return HttpResponse("Invalid verification code.")
            else:
                return HttpResponse("Email does not match the pending registration.")
        else:
            return HttpResponse("No pending registration found for this email.")
    return render(request, "account/verify_email.html")
