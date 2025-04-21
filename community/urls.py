from . import views
from django.urls import path
from .views import edit_post


urlpatterns = [
    path('', views.community_forum, name='community_forum'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', edit_post, name='edit_post'),
    path('save-post/<int:post_id>/', views.save_post, name='save_post'),

]
