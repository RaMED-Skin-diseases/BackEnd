# models.py

from django.db import models
from account.models import User
from storages.backends.s3boto3 import S3Boto3Storage


class CommunityImageStorage(S3Boto3Storage):
    location = 'community_images'
    file_overwrite = False
    default_acl = 'private'  # Or 'private' if you prefer


class CommunityPost(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    image = models.ImageField(
        upload_to='community_images/',
        storage=CommunityImageStorage(),  # Add this line
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    class Meta:
        verbose_name = "Community Post"
        verbose_name_plural = "Community Posts"


class Comment(models.Model):
    post = models.ForeignKey(
        CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    def save(self, *args, **kwargs):
        if self.author.user_type != 'Doctor':
            raise ValueError("Only doctors are allowed to comment.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
