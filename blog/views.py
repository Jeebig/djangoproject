from django.shortcuts import render
from .models import Post

def index(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/index.html', {
        'title': 'Blog Home',
        'posts': posts,
        'user': request.user,
    })