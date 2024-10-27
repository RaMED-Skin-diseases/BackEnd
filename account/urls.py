from . import views
from django.urls import path


urlpatterns = [
    path("signup", views.signup, name='signup'),
    path("verify_email", views.verify_email, name='verify_email'),
]
