from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from typing import Optional
from .forms import CustomUserCreationForm
from .models import User
from blog.models import Post, Comment

def register_view(request: HttpRequest) -> HttpResponse:
    """Представление для регистрации новых пользователей с кастомной моделью User"""
    if request.user.is_authenticated:
        # Если пользователь уже авторизован, перенаправляем на главную
        return redirect('blog:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически входим после регистрации
            login(request, user)
            
            # Добавляем сообщение об успешной регистрации
            messages.success(
                request, 
                f'Добро пожаловать, {user.first_name or user.username}! Вы успешно зарегистрированы и вошли в систему.'
            )
            
            # Перенаправляем на главную страницу
            return redirect('blog:index')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'accounts/register.html', context)

def logout_view(request: HttpRequest) -> HttpResponse:
    """Кастомный logout view, который принимает GET и POST запросы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('blog:index')

def profile_view(request: HttpRequest, username: Optional[str] = None) -> HttpResponse:
    """Отображение профиля пользователя"""
    
    if username:
        # Если передан username, показываем профиль другого пользователя (публично доступно)
        user = get_object_or_404(User, username=username)
        is_own_profile = request.user.is_authenticated and request.user == user
    else:
        # Если username не передан, показываем профиль текущего пользователя (требует авторизации)
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        user = request.user
        is_own_profile = True
    
    # Получаем посты пользователя
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    
    # Получаем комментарии пользователя
    user_comments = Comment.objects.filter(author=user, is_active=True).order_by('-created_at')[:5]
    
    # Статистика
    posts_count = user_posts.count()
    comments_count = Comment.objects.filter(author=user, is_active=True).count()
    
    context = {
        'title': f'Профиль {user.get_full_name() or user.username}',
        'profile_user': user,
        'is_own_profile': is_own_profile,
        'user_posts': user_posts,
        'user_comments': user_comments,
        'posts_count': posts_count,
        'comments_count': comments_count,
    }
    return render(request, 'accounts/profile.html', context)
