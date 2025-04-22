from django.urls import path
from .views import send_image_to_api, my_diagnoses, delete_diagnosis

urlpatterns = [
    path("upload-image/", send_image_to_api, name="upload-image"),
    path("my-diagnoses/", my_diagnoses, name="my-diagnoses"),
    path('delete-diagnosis/<int:diagnosis_id>/', delete_diagnosis, name='delete_diagnosis'),

]
