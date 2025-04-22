from django.db import models
from account.models import User
from storages.backends.s3boto3 import S3Boto3Storage

# Reuse the CommunityImageStorage for diagnosis images
class DiagnosisImageStorage(S3Boto3Storage):
    location = 'model_images'  # Store images in the same location as community images
    file_overwrite = False
    default_acl = 'private'


class Diagnosis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='diagnosis_images/', storage=DiagnosisImageStorage(), blank=True, null=True)
    diagnosis_result = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis {self.id} for {self.user.username}"

    class Meta:
        verbose_name = "Diagnosis"
        verbose_name_plural = "Diagnoses"
