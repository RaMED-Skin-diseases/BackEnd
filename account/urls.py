from . import views
from django.urls import path, re_path


urlpatterns = [
    path("signup", views.signup, name='signup'),
    path("verify_email", views.verify_email, name='verify_email'),
    path("login", views.login, name='login'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('resend_verification_code/<slug:username>', views.resend_verification_code, name='resend_verification_code'),
    re_path(r'^resend_verification_code/(?P<username>[\w.@+-]+)/$', views.resend_verification_code, name='resend_verification_code'),
    path('profile/<slug:username>', views.view_profile, name='profile'),
    re_path(r'^profile/(?P<username>[\w.@+-]+)/$', views.view_profile, name='profile'),
    # path('home', views.home, name='home'),
    path('logout', views.logout, name='logout'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('community/', views.community_forum, name='community_forum'),
    path('community/create/', views.create_post, name='create_post'),
    path('community/post/<int:post_id>/', views.post_detail, name='post_detail'),
]
