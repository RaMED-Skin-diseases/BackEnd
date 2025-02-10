# forms.py
from django import forms
from .models import CommunityPost, Comment

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']