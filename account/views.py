from django.utils import timezone
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import User, CommunityPost, Comment
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CommunityPostForm, CommentForm


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
            return JsonResponse({'error': 'Email already exists'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        try:
            MinLengthValidator(8)(password)
        except ValidationError:
            return JsonResponse({'error': 'Password must be at least 8 characters long.'}, status=400)
        try:
            MinLengthValidator(3)(username)
            RegexValidator(r'^(?=.*[a-zA-Z])[a-zA-Z0-9._-]*$',
                           message="Username must include at least one letter and can only contain '.', '_', or '-'")(username)
        except ValidationError:
            return JsonResponse({'error': 'Username must be at least 3 characters long and include letters.'}, status=400)
        try:
            RegexValidator(r'^[a-zA-Z]+$')(f_name)
        except ValidationError:
            return JsonResponse({'error': 'First name must contain only letters.'}, status=400)
        try:
            RegexValidator(r'^[a-zA-Z]+$')(l_name)
        except ValidationError:
            return JsonResponse({'error': 'Last name must contain only letters.'}, status=400)

        user = User(
            f_name=f_name,
            l_name=l_name,
            date_of_birth=date_of_birth,
            email=email,
            gender=gender,
            password=make_password(password),
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
            return JsonResponse({'message': 'User registered successfully. Please check your email for the verification code.'}, status=200)
        except Exception as e:
            user.delete()
            return JsonResponse({'error': 'Failed to send email. Please try again later.'}, status=400)
    return render(request, "account/signup.html")


@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        email_username = request.POST.get("email").lower()
        code = request.POST.get("verification_code")
        expiry_time = timezone.timedelta(minutes=10)
        try:
            user = User.objects.filter(email=email_username, verification_code=code).first() or \
                User.objects.filter(username=email_username,
                                    verification_code=code).first()
            if user.code_created_at and timezone.now() - user.code_created_at < expiry_time:
                user.is_verified = True
                user.verification_code = None
                user.code_created_at = None
                user.save()
                return JsonResponse({'message': 'Email verified successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid verification code or code has expired.'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid verification code or email.'}, status=400)
    return render(request, "account/verify_email.html")


def resend_verification_code(request, username):
    if request.method == "GET":
        username = username.lower()
        if not User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User not found.'}, status=404)
        try:
            send_verification_code(username)
            return JsonResponse({'message': 'Verification code sent. Please check your email.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Failed to send email. Please try again later.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def send_verification_code(username):
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': 'User not found.'}, status=404)
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.code_created_at = timezone.now()
        user.save()
        email_code(user)
        return JsonResponse({'message': 'Verification code sent. Please check your email.'}, status=200)
    except Exception as e:
        return str(e)


@csrf_exempt
def login(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        password = request.POST.get("password")

        user = User.objects.filter(username=username_email).first(
        ) or User.objects.filter(email=username_email).first()

        if user is None:
            return JsonResponse({'error': 'Invalid username or email.'}, status=400)

        if user.is_verified:
            if check_password(password, user.password):
                auth_login(request, user)
                return JsonResponse({'message': 'Logged in successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid password.'}, status=400)
        else:
            return redirect('verify_email')

    return render(request, "account/login.html")


@csrf_exempt
def forgot_password(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        print(username_email)
        try:
            user = User.objects.filter(email=username_email).first() or User.objects.filter(
                username=username_email).first()
            send_verification_code(user.username)
            return JsonResponse({'message': 'Verification code sent. Please check your email.'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or username.'}, status=400)
    return render(request, "account/forgot_password.html")


@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        username_email = request.POST.get("username_email").lower()
        verification_code = request.POST.get("verification_code")
        new_password = request.POST.get("new_password")

        try:
            user = User.objects.filter(email=username_email, verification_code=verification_code).first() or \
                User.objects.filter(username=username_email,
                                    verification_code=verification_code).first()
            expiry_time = timezone.timedelta(minutes=10)

            # Check if the reset code is still valid
            if user.code_created_at and timezone.now() - user.code_created_at < expiry_time:
                # Validate the new password
                try:
                    MinLengthValidator(8)(new_password)
                except ValidationError:
                    return JsonResponse({'error': 'Password must be at least 8 characters long.'}, status=400)

                # Save the new password and clear reset code
                user.password = make_password(new_password)
                user.verification_code = None
                user.code_created_at = None
                user.save()
                return JsonResponse({'message': 'Password reset successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid reset code or code has expired.'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid reset code or email.'}, status=400)
    return render(request, "account/reset_password.html")


def view_profile(request, username):
    if request.method == "GET":
        username = username.lower()
        user = User.objects.filter(username=username).first()

        if user:
            get_user_info = [user.f_name, user.l_name, user.date_of_birth, user.gender, user.username, user.email, user.user_type, user.is_verified, user.info,
                             user.specialization, user.clinic_details]
            comma_separated = ', '.join(map(str, get_user_info))
            return JsonResponse({'user': comma_separated}, status=200)
        else:
            return JsonResponse({'error': 'User not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


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
    auth_logout(request)
    return JsonResponse({'message': 'Logged out successfully.'}, status=200)


@csrf_exempt
@login_required
def edit_profile(request):

    user = request.user

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
            return JsonResponse({'error': 'First name must contain only letters.'}, status=400)

        try:
            RegexValidator(r'^[a-zA-Z]+$')(l_name)
        except ValidationError:
            return JsonResponse({'error': 'Last name must contain only letters.'}, status=400)

        if User.objects.filter(email=email).exists() and user.email != email:
            return JsonResponse({'error': 'Email already exits'}, status=400)
        if User.objects.filter(username=username).exists() and user.username != username:
            return JsonResponse({'error': 'Username already exits'}, status=400)

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
            return JsonResponse({'message': 'Verification code sent successfully.'}, status=200)

        # Redirect to profile view or home
        return redirect('profile', username=user.username)
    return render(request, "account/edit_profile.html", {"user": user})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('community_forum')
    else:
        form = CommunityPostForm()
    return render(request, 'account/create_post.html', {'form': form})


@login_required
def community_forum(request):
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, 'account/community_forum.html', {'posts': posts})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'account/post_detail.html', {'post': post, 'comments': comments, 'form': form})