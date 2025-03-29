from django.urls import path
from .views import send_image_to_api

urlpatterns = [
    path("upload-image/", send_image_to_api, name="upload-image"),
]
