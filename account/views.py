from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Signup_patient, Signup_doc
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@csrf_exempt
def signup_patient(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        age = request.POST.get("age")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username")

        patient = Signup_patient(
            f_name=f_name,
            l_name=l_name,
            age=age,
            email=email,
            gender=gender,
            password=password,
            username=username,
        )
        patient.save()
        return HttpResponse("Patient registered successfully")
    return render(request, "account/signup_patient.html")

@csrf_exempt
def signup_doc(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        age = request.POST.get("age")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username")
        info = request.POST.get("info")
        specialization = request.POST.get("specialization")
        clinic_details = request.POST.get("clinic_details")

        doctor = Signup_doc(
            f_name=f_name,
            l_name=l_name,
            age=age,
            email=email,
            gender=gender,
            password=password,
            username=username,
            info=info,
            specialization=specialization,
            clinic_details=clinic_details,
        )
        doctor.save()
        return HttpResponse("Doctor registered successfully")
    return render(request, "account/signup_doc.html")
