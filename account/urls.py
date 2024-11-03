from . import views
from django.urls import path


urlpatterns = [
    path("signup", views.signup, name='signup'),
    path("verify_email", views.verify_email, name='verify_email'),
    path("login", views.login, name='login'),
    path('password-reset', views.password_reset, name='password_reset'),
]
