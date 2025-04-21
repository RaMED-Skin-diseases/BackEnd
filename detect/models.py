from django.db import models
from django.contrib.auth.models import User

class Diagnosis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnoses')
    image = models.ImageField(upload_to='diagnoses/')
    diagnosis_result = models.TextField()  # Store the diagnosis result (JSON)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis for {self.user.username} on {self.created_at}"
