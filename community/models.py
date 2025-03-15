from django.db import models
from account.models import User

# Create your models here.
class CommunityPost(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    image = models.ImageField(
        upload_to='community_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

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
        # Ensure only doctors can comment
        if self.author.user_type != 'Doctor':
            raise ValueError("Only doctors are allowed to comment.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
