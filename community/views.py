from django.shortcuts import render
from django.http import JsonResponse
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import CommunityPost
from .forms import CommunityPostForm, CommentForm


# Create your views here.

@csrf_exempt
@login_required
def create_post(request):
    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Post created successfully.',
                'post_id': post.id,
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data.',
                'errors': form.errors,
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.',
        }, status=405)


@login_required
def community_forum(request):
    posts = CommunityPost.objects.all().order_by('-created_at')
    posts_data = serialize('json', posts, fields=(
        'title', 'content', 'image', 'created_at', 'author'))
    return JsonResponse({
        'status': 'success',
        'posts': posts_data,
    }, safe=False)


@csrf_exempt
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
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
        'image': post.image.url if post.image else None,
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
