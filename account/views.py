from django.utils import timezone
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Signup_patient, Signup_doc
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
def signup_patient(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        date_of_birth = request.POST.get("date_of_birth")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username")
        verification_code = generate_verification_code()

        if Signup_patient.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")
        if Signup_patient.objects.filter(username=username).exists():
            return HttpResponse("Username already exists.")

        request.session['patient_data'] = {
            'f_name': f_name,
            'l_name': l_name,
            'date_of_birth': date_of_birth,
            'email': email,
            'gender': gender,
            'password': password,
            'username': username,
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
        return HttpResponse("Patient registered successfully. Please check your email for the verification code.")
    return render(request, "account/signup_patient.html")


@csrf_exempt
def verify_patient_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("verification_code")
        patient_data = request.session.get('patient_data')

        if patient_data:
            if 'email' in patient_data and patient_data['email'] == email:
                if patient_data['verification_code'] == code:
                    code_created_at = datetime.strptime(
                        patient_data['code_created_at'], '%Y-%m-%d %H:%M:%S')
                    code_created_at = timezone.make_aware(code_created_at)
                    if timezone.now() - code_created_at < timezone.timedelta(minutes=5):
                        patient = Signup_patient(
                            f_name=patient_data['f_name'],
                            l_name=patient_data['l_name'],
                            date_of_birth=patient_data['date_of_birth'],
                            email=patient_data['email'],
                            gender=patient_data['gender'],
                            password=patient_data['password'],
                            username=patient_data['username'],
                            is_verified=True,
                        )
                        patient.save()
                        del request.session['patient_data']
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


@csrf_exempt
def signup_doc(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        date_of_birth = request.POST.get("date_of_birth")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username")
        info = request.POST.get("info")
        specialization = request.POST.get("specialization")
        clinic_details = request.POST.get("clinic_details")
        verification_code = generate_verification_code()

        if Signup_doc.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")
        if Signup_doc.objects.filter(username=username).exists():
            return HttpResponse("Username already exits.")

        request.session['doctor_data'] = {
            'f_name': f_name,
            'l_name': l_name,
            'date_of_birth': date_of_birth,
            'email': email,
            'gender': gender,
            'password': password,
            'username': username,
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
        return HttpResponse("Doctor registered successfully. Please check your email for the verification code.")
    return render(request, "account/signup_doc.html")


@csrf_exempt
def verify_doctor_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("verification_code")
        doctor_data = request.session.get('doctor_data')

        if doctor_data:
            if 'email' in doctor_data and doctor_data['email'] == email:
                if doctor_data['verification_code'] == code:
                    code_created_at = datetime.strptime(
                        doctor_data['code_created_at'], '%Y-%m-%d %H:%M:%S')
                    code_created_at = timezone.make_aware(code_created_at)
                    if timezone.now() - code_created_at < timezone.timedelta(minutes=5):
                        doctor = Signup_doc(
                            f_name=doctor_data['f_name'],
                            l_name=doctor_data['l_name'],
                            date_of_birth=doctor_data['date_of_birth'],
                            email=doctor_data['email'],
                            gender=doctor_data['gender'],
                            password=doctor_data['password'],
                            username=doctor_data['username'],
                            info=doctor_data['info'],
                            specialization=doctor_data['specialization'],
                            clinic_details=doctor_data['clinic_details'],
                            is_verified=True,
                        )
                        doctor.save()
                        del request.session['doctor_data']
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
