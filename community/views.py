# views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import CommunityPost,SavedPost
from .forms import CommunityPostForm, CommentForm
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    form = CommunityPostForm(request.data, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Post created successfully.',
            'post_id': post.id,
            'image_url': post.get_image_url(),
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid form data.',
            'errors': form.errors,
        }, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def community_forum(request):
    sort_by = request.GET.get('sort_by', '-created_at')
    search_query = request.GET.get('search', '')

    posts = CommunityPost.objects.all()
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query) |
            Q(comments__content__icontains=search_query) |
            Q(comments__author__username__icontains=search_query) |
            Q(comments__author__first_name__icontains=search_query) |
            Q(comments__author__last_name__icontains=search_query)
        )

    posts = posts.order_by(sort_by)
    posts_data = []
    for post in posts:
        is_saved = False
        if request.user.is_authenticated:
            is_saved = SavedPost.objects.filter(user=request.user, post=post).exists()
    
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'image': post.get_image_url(),
            'created_at': post.created_at,
            'author': post.author.username,
            'is_saved': is_saved,  # 👈 New field!
        })


    return JsonResponse({
        'status': 'success',
        'posts': posts_data,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.data)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Comment added successfully.',
                'comment_id': comment.id,
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data.',
                'errors': form.errors,
            }, status=400)

    post_data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'image': post.get_image_url(),
        'created_at': post.created_at,
        'author': post.author.username,
    }

    comments_data = [
        {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at,
            'author': comment.author.username,
        }
        for comment in comments
    ]

    return JsonResponse({
        'status': 'success',
        'post': post_data,
        'comments': comments_data,
    })
    
    
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)

    if post.author != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'You are not allowed to edit this post.'
        }, status=403)

    data = request.data.copy()

    # If 'title' or 'content' is missing, use the existing ones
    if 'title' not in data:
        data['title'] = post.title
    if 'content' not in data:
        data['content'] = post.content

    form = CommunityPostForm(data, request.FILES, instance=post)

    if form.is_valid():
        updated_post = form.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Post updated successfully.',
            'post_id': updated_post.id,
            'title': updated_post.title,
            'content': updated_post.content,
            'image_url': updated_post.get_image_url(),
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid form data.',
            'errors': form.errors,
        }, status=400)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    user = request.user

    saved, created = SavedPost.objects.get_or_create(user=user, post=post)
    if not created:
        # Already saved → unsave it
        saved.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Post unsaved.'
        })

    return JsonResponse({
        'status': 'success',
        'message': 'Post saved.'
    })
