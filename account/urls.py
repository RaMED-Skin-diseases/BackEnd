from . import views
from django.urls import path


urlpatterns = [
    path("signup_patient", views.signup_patient, name='signup_patient'),
    path("signup_doc", views.signup_doc, name='signup_doc'),
]
