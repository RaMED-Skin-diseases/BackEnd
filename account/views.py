from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def signup_patient(request):
    return HttpResponse("welcome")


def signup_doc(request):
    return HttpResponse("welcome dr")
