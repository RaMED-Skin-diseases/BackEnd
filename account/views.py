from django.utils import timezone
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator


# Create your views here.

def generate_verification_code(length=6):
    """Generate a random verification code of given length."""
    return ''.join(random.choices(string.digits, k=length))


def email_code(user):
    subject = 'Verification Code'
    message = (
        f"Hi Dr. {user.f_name} {user.l_name},\n\n"
        f"Use the following code to verify your email address:\n\n"
        f"{user.verification_code}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"Regards,\nSkinWise Team"
    ) if user.user_type == "Doctor" else (
        f"Hi {user.f_name} {user.l_name},\n\n"
        f"Use the following code to verify your email address:\n\n"
        f"{user.verification_code}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"Regards,\nSkinWise Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
              [user.email], fail_silently=False)


@csrf_exempt
def signup(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        date_of_birth = request.POST.get("date_of_birth")
        email = request.POST.get("email").lower()
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        username = request.POST.get("username").lower()
        user_type = request.POST.get("user_type")
        info = request.POST.get("info")
        specialization = request.POST.get("specialization")
        clinic_details = request.POST.get("clinic_details")

        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exits.")
        try:
            MinLengthValidator(8)(password)
        except ValidationError:
            return HttpResponse("Password must be at least 8 characters long.")
        try:
            MinLengthValidator(3) and RegexValidator(
                RegexValidator(r'^(?=.*[a-zA-Z])[a-zA-Z0-9._-]*$'))(username)
        except ValidationError:
            return HttpResponse("Username must be at least 3 characters long and include letters.")
        try:
            RegexValidator(r'^[a-zA-Z]+$')(f_name)
        except ValidationError:
            return HttpResponse("First name must contain only letters.")
        try:
            RegexValidator(r'^[a-zA-Z]+$')(l_name)
        except ValidationError:
            return HttpResponse("Last name must contain only letters.")

        user = User(
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
            is_verified=False,
        )
        user.save()

        try:
            send_verification_code(user.username)
            return HttpResponse("User registered successfully. Please check your email for the verification code.")
        except Exception as e:
            user.delete()
            return HttpResponse("Failed to send email. Please try again later.")
    return render(request, "account/signup.html")


@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        email_username = request.POST.get("email").lower()
        code = request.POST.get("verification_code")
        expiry_time = timezone.timedelta(minutes=10)
        try:
            user = User.objects.get(
                email=email_username, verification_code=code) or User.objects.get(
                    username=email_username, verification_code=code)
            if timezone.now() - user.code_created_at < expiry_time:
                user.is_verified = True
                user.verification_code = None
                user.code_created_at = None
                user.save()
                return HttpResponse("Email verified successfully. You are now registered.")
            else:
                return HttpResponse("Verification code has expired.")
        except User.DoesNotExist:
            return HttpResponse("User not found or invalid verification code.")
    return render(request, "account/verify_email.html")


def resend_verification_code(request, username):
    if request.method == "GET":
        username = username.lower()
        try:
            send_verification_code(username)
            return HttpResponse("Verification code sent. Please check your email.")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return HttpResponse("Invalid request method.")


def send_verification_code(username):
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            return HttpResponse("User not found.", status=404)
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.code_created_at = timezone.now()
        user.save()
        email_code(user)
        return HttpResponse("Verification code sent. Please check your email.")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


@csrf_exempt
def login(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        password = request.POST.get("password")

        user = User.objects.filter(username=username_email).first(
        ) or User.objects.filter(email=username_email).first()

        if user is None:
            return HttpResponse("User not found.")

        if user.is_verified:
            if user and user.password == password:
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['user_type'] = user.user_type
                # return redirect('home')
                return HttpResponse("Login successful.")
            else:
                return HttpResponse("Invalid credentials.")
        else:
            return redirect('verify_email')

    return render(request, "account/login.html")


@csrf_exempt
def forgot_password(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        try:
            user = User.objects.filter(email=username_email).first() or User.objects.filter(
                username=username_email).first()
            send_verification_code(user.username)
            return HttpResponse("Password reset code sent. Please check your email.")
        except User.DoesNotExist:
            return HttpResponse("Email not found.")
    return render(request, "account/forgot_password.html")


@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        verification_code = request.POST.get("verification_code")
        new_password = request.POST.get("new_password")

        try:
            user = User.objects.filter(email=username_email, verification_code=verification_code).first() or User.objects.filter(
                username=username_email, verification_code=verification_code).first()
            expiry_time = timezone.timedelta(minutes=10)

            # Check if the reset code is still valid
            if timezone.now() - user.code_created_at < expiry_time:
                # Validate the new password
                try:
                    MinLengthValidator(8)(new_password)
                except ValidationError:
                    return HttpResponse("Password must be at least 8 characters long.")

                # Save the new password and clear reset code
                user.password = new_password
                user.verification_code = None
                user.code_created_at = None
                user.save()
                return HttpResponse("Password reset successful.")
            else:
                return HttpResponse("Reset code has expired.")
        except User.DoesNotExist:
            return HttpResponse("Invalid reset code or email.")
    return render(request, "account/reset_password.html")


def view_profile(request, username):
    if request.method == "GET":
        username = username.lower()
        user = User.objects.filter(username=username).first()
        get_user_info = [user.f_name, user.l_name, user.date_of_birth, user.gender, user.username, user.email, user.user_type, user.info,
                         user.specialization, user.clinic_details, user.is_verified]
        comma_separated = ', '.join(map(str, get_user_info))
        if user:
            return HttpResponse(comma_separated)
        else:
            return HttpResponse("User not found.")
    return HttpResponse("Invalid request method.")


# def home(request):
#     # Check if user is logged in
#     if 'user_id' not in request.session:
#         # If not logged in, redirect to login page
#         return redirect('login')

#     # Fetch user details from session
#     user_id = request.session['user_id']
#     user = User.objects.get(id=user_id)

#     # Prepare context for the home page
#     context = {
#         'user': user,
#         'user_type': user.user_type,
#         'username': user.username
#     }

#     return render(request, "account/home.html", context)


def logout(request):
    request.session.flush()
    return HttpResponse("Logged out successfully.")


@csrf_exempt
def edit_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        email = request.POST.get("email")
        username = request.POST.get("username")

        try:
            RegexValidator(r'^[a-zA-Z]+$')(f_name)
        except ValidationError:
            return HttpResponse("First name must contain only letters.")

        try:
            RegexValidator(r'^[a-zA-Z]+$')(l_name)
        except ValidationError:
            return HttpResponse("Last name must contain only letters.")

        if User.objects.filter(email=email).exists() and user.email != email:
            return HttpResponse("Email already exists.")
        if User.objects.filter(username=username).exists() and user.username != username:
            return HttpResponse("Username already exits.")

        old_email = user.email

        user.f_name = f_name
        user.l_name = l_name
        user.date_of_birth = date_of_birth
        user.gender = gender
        user.username = username
        user.email = email

        # If user is a doctor, allow updating additional fields
        if user.user_type == "Doctor":
            info = request.POST.get("info")
            specialization = request.POST.get("specialization")
            clinic_details = request.POST.get("clinic_details")
            user.specialization = specialization
            user.clinic_details = clinic_details
            user.info = info

        # Save the updated user
        user.save()

        if old_email != email:
            user.is_verified = False
            user.verification_code = None
            user.code_created_at = None
            user.save()
            send_verification_code(user.username)
            return HttpResponse("Profile updated successfully. Please verify your email address.")

        # Redirect to profile view or home
        return redirect('profile', username=user.username)
    return render(request, "account/edit_profile.html", {"user": user})
