from . import views
from django.urls import path


urlpatterns = [
    path('', views.community_forum, name='community_forum'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),

]
