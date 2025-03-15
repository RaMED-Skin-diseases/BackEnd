from django.urls import path
from .views import test_upload_page, predict_skin_disease

urlpatterns = [
    path("predict/", predict_skin_disease, name="predict_skin_disease"),
    path("test/", test_upload_page, name="test_upload_page"),  # New test page
]
