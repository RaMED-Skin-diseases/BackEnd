from . import views
from django.urls import path


urlpatterns = [
    path("signup", views.signup, name='signup'),
    path("verify_email", views.verify_email, name='verify_email'),
    path("login", views.login, name='login'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('resend_verification_code/<slug:username>', views.resend_verification_code, name='resend_verification_code'),
    path('profile/<slug:username>', views.view_profile, name='profile'),
]
