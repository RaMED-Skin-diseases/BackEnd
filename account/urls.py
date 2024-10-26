from . import views
from django.urls import path


urlpatterns = [
    path("signup_patient", views.signup_patient, name='signup_patient'),
    path("signup_doc", views.signup_doc, name='signup_doc'),
    path("verify_patient_email", views.verify_patient_email, name='verify_patient_email'),
    path("verify_doctor_email", views.verify_doctor_email, name='verify_doctor_email'),
]
