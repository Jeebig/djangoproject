from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from typing import Any, Dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy

from blog.forms import PostForm, CommentForm
from .models import Category, Post, Comment, Tag


def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 3)  # Show 3 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': "Blog Home",
        # Используем пагинированные посты
        'posts': page_obj,
        'page_obj': page_obj,
    }
    context.update(get_categories())
    return render(request, "blog/index.html", context=context)


def favorite_song(request: HttpRequest) -> HttpResponse:
    context = {
        'song_line': "You made me a, you made me a believer, believer",
        'artist': "Imagine Dragons",
        'title': "Believer"
    }
    return render(request, 'blog/favorite_song.html', context)


def about_me(request: HttpRequest) -> HttpResponse:
    context = {
        'title': "About Me",
        'name': "Your Name",
        'description': "This is about me page"
    }
    return render(request, 'blog/about.html', context)


def contact_me(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Обработка отправленной формы
        name = request.POST.get('name')
        # email = request.POST.get('email')  # Можно использовать для отправки email
        # message = request.POST.get('message')  # Можно сохранить в БД
        
        # Здесь можно добавить логику отправки email или сохранения в БД
        # Пока просто покажем сообщение об успехе
        context = {
            'title': "Contact Me",
            'email': "your.email@example.com",
            'success_message': f"Thank you {name}! Your message has been received.",
            'form_submitted': True
        }
    else:
        context = {
            'title': "Contact Me",
            'email': "your.email@example.com"
        }
    return render(request, 'blog/contact.html', context)


def my_works(request: HttpRequest) -> HttpResponse:
    context = {
        'title': "My Works",
        'works': ["Project 1", "Project 2", "Project 3"]
    }
    return render(request, 'blog/my_works.html', context)


def favorite_works(request: HttpRequest) -> HttpResponse:
    context = {
        'title': "Favorite Works",
        'favorites': ["Favorite 1", "Favorite 2"]
    }
    return render(request, 'blog/favorite_works.html', context)


def skills(request: HttpRequest) -> HttpResponse:
    context = {
        'title': "My Skills",
        'programming_skills': [
            {'name': 'Python', 'level': 'Advanced', 'experience': '3+ years'},
            {'name': 'Django', 'level': 'Intermediate', 'experience': '2+ years'},
            {'name': 'JavaScript', 'level': 'Intermediate', 'experience': '2+ years'},
            {'name': 'HTML/CSS', 'level': 'Advanced', 'experience': '4+ years'},
            {'name': 'Bootstrap', 'level': 'Advanced', 'experience': '3+ years'},
        ],
        'tools': ['Git', 'VS Code', 'PostgreSQL', 'SQLite', 'Docker'],
        'soft_skills': ['Problem Solving', 'Team Work', 'Communication', 'Time Management']
    }
    return render(request, 'blog/skills.html', context)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:  # 404 handler
    return render(request, 'blog/404.html', status=404)

def server_error(request: HttpRequest) -> HttpResponse:  # 500 handler
    return render(request, 'blog/500.html', status=500)

def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post_obj = get_object_or_404(Post.objects.select_related('author', 'category').prefetch_related('tags'), pk=pk)
    # Получаем комментарии используя обратную связь
    comments = Comment.objects.filter(post=post_obj, is_active=True).select_related('author').order_by('created_at')
    
    # Обработка формы комментариев
    comment_form = CommentForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post_obj
                comment.author = request.user
                comment.save()
                # Перенаправляем на ту же страницу, чтобы избежать повторной отправки формы
                return redirect('blog:post-detail-slug', slug=post_obj.slug)
        else:
            # Если пользователь не авторизован, перенаправляем на страницу входа
            return redirect('accounts:login')
    
    # Навигация между постами
    try:
        previous_post = Post.objects.filter(created_at__lt=post_obj.created_at).order_by('-created_at').first()
    except Post.DoesNotExist:
        previous_post = None
    
    try:
        next_post = Post.objects.filter(created_at__gt=post_obj.created_at).order_by('created_at').first()
    except Post.DoesNotExist:
        next_post = None
    
    context = {
        'title': post_obj.title,
        'post': post_obj,
        'tags': post_obj.tags.all(),
        'comments': comments,
        'comment_form': comment_form,
        'previous_post': previous_post,
        'next_post': next_post,
    }
    context.update(get_categories())
    return render(request, 'blog/post.html', context)

def post_detail_by_slug(request: HttpRequest, slug: str) -> HttpResponse:
    post_obj = get_object_or_404(Post.objects.select_related('author', 'category').prefetch_related('tags'), slug=slug)
    # Получаем комментарии используя обратную связь
    comments = Comment.objects.filter(post=post_obj, is_active=True).select_related('author').order_by('created_at')
    
    # Обработка формы комментариев
    comment_form = CommentForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post_obj
                comment.author = request.user
                comment.save()
                # Перенаправляем на ту же страницу, чтобы избежать повторной отправки формы
                return redirect('blog:post-detail-slug', slug=slug)
        else:
            # Если пользователь не авторизован, перенаправляем на страницу входа
            return redirect('accounts:login')
    
    # Навигация между постами
    try:
        previous_post = Post.objects.filter(created_at__lt=post_obj.created_at).order_by('-created_at').first()
    except Post.DoesNotExist:
        previous_post = None
    
    try:
        next_post = Post.objects.filter(created_at__gt=post_obj.created_at).order_by('created_at').first()
    except Post.DoesNotExist:
        next_post = None
    
    context = {
        'title': post_obj.title,
        'post': post_obj,
        'tags': post_obj.tags.all(),
        'comments': comments,
        'comment_form': comment_form,
        'previous_post': previous_post,
        'next_post': next_post,
    }
    context.update(get_categories())
    return render(request, 'blog/post.html', context)


def get_categories():
    all_categories = Category.objects.all()
    half = all_categories.count() // 2
    first_half = all_categories[:half]
    second_half = all_categories[half:]
    return {
        'categories': all_categories,
        'first_half': first_half, 
        'second_half': second_half
    }
    

from typing import Dict, Any

def category_posts(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).select_related('author').prefetch_related('tags').order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(posts, 3)  # 3 поста на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context: Dict[str, Any] = {
        'title': f"Posts in {category.name}",
        'category': category,
        'posts': page_obj,
        'page_obj': page_obj,
    }
    context.update(get_categories())
    return render(request, 'blog/category_posts.html', context)

def tag_posts(request: HttpRequest, tag_name: str) -> HttpResponse:
    """Отображает посты с определенным тегом"""
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(tags=tag).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context: Dict[str, Any] = {
        'title': f"Posts tagged with '{tag.name}'",
        'tag': tag,
        'posts': page_obj,
        'page_obj': page_obj,
    }
    context.update(get_categories())
    return render(request, 'blog/tag_posts.html', context)

def search_posts(request: HttpRequest) -> HttpResponse:
    """Поиск постов по заголовку и содержимому"""
    query = request.GET.get('q', '').strip()
    posts = []
    
    if query:
        # Регистронезависимый поиск по заголовку и содержимому
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
        
        # Пагинация результатов поиска
        paginator = Paginator(posts, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        posts = page_obj
    else:
        page_obj = None
    
    context: Dict[str, Any] = {
        'title': f"Результаты поиска: '{query}'" if query else "Поиск",
        'posts': posts,
        'page_obj': page_obj,
        'query': query,
    }
    context.update(get_categories())
    return render(request, 'blog/search_results.html', context)

# @login_required
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        form.save_m2m()
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(get_categories())
        return context
