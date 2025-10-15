from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from typing import Optional, Dict, Any, Set, cast
from .forms import CustomUserCreationForm
from .models import User, Follow, Notification
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
    
    context: Dict[str, Any] = {
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
        user: User = get_object_or_404(User, username=username)  # explicit type for static analysis
        is_own_profile = request.user.is_authenticated and request.user == user
    else:
        # Если username не передан, показываем профиль текущего пользователя (требует авторизации)
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        user = cast(User, request.user)
        is_own_profile = True
    
    # Получаем посты пользователя
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    
    # Получаем комментарии пользователя
    user_comments = Comment.objects.filter(author=user, is_active=True).order_by('-created_at')[:5]
    
    # Статистика
    posts_count = user_posts.count()
    comments_count = Comment.objects.filter(author=user, is_active=True).count()
    
    # Информация о подписках
    followers_count: int = user.get_followers_count()  # type: ignore[attr-defined]
    following_count: int = user.get_following_count()  # type: ignore[attr-defined]
    is_following: bool = False
    following_ids: Set[int] = set()

    if request.user.is_authenticated:
        # is current user following the profile user (only relevant if viewing others)
        if not is_own_profile:
            is_following = user.followers.filter(follower=request.user).exists()  # type: ignore[attr-defined]
        # build a set of ids current user is following for template checks
        current_user = cast(User, request.user)
        following_ids = set(current_user.following.values_list('following__id', flat=True))  # type: ignore[attr-defined]
    
    context: Dict[str, Any] = {
        'title': f'Профиль {user.get_full_name() or user.username}',
        'profile_user': user,
        'is_own_profile': is_own_profile,
        'user_posts': user_posts,
        'user_comments': user_comments,
        'posts_count': posts_count,
        'comments_count': comments_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'following_ids': following_ids,
    }
    return render(request, 'accounts/profile.html', context)


def follow_toggle_view(request: HttpRequest, username: str) -> HttpResponse:
    """Переключение подписки на пользователя"""
    if not request.user.is_authenticated:
        login_url = reverse('accounts:login')
        next_url = reverse('accounts:profile-user', kwargs={'username': username})
        return redirect(f"{login_url}?next={next_url}")
    
    if request.method != 'POST':
        return redirect('accounts:profile-user', username=username)
    
    user_to_follow: User = get_object_or_404(User, username=username)  # type: ignore[assignment]
    
    # Нельзя подписаться на самого себя
    if user_to_follow == request.user:
        # Больше не показываем всплывающие сообщения, просто редирект
        return redirect('accounts:profile-user', username=username)
    
    # Проверяем, есть ли уже подписка
    follow_obj = Follow.objects.filter(follower=request.user, following=user_to_follow).first()
    
    if follow_obj:
        # Если подписка есть - отписываемся
        follow_obj.delete()
    else:
        # Если подписки нет - подписываемся (уведомление создаст сигнал)
        Follow.objects.create(follower=request.user, following=user_to_follow)
    
    return redirect('accounts:profile-user', username=username)


def notifications_view(request: HttpRequest) -> HttpResponse:
    """Список уведомлений для текущего пользователя"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Вычитываем список и одновременно отмечаем непрочитанные как прочитанные
    notifs_qs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # сначала получим список, чтобы отрендерить уже обновлённые статусы
    notifs = list(notifs_qs)
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    context: Dict[str, Any] = {
        'title': 'Уведомления',
        'notifications': notifs,
    }
    return render(request, 'accounts/notifications.html', context)


def notifications_mark_read(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('accounts:notifications')


def followers_view(request: HttpRequest, username: str) -> HttpResponse:
    """Список подписчиков пользователя"""
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower')
    
    # ids that current user follows, used in template to render button state
    following_ids: Set[int] = set()
    if request.user.is_authenticated:
        current_user = cast(User, request.user)
        following_ids = set(current_user.following.values_list('following__id', flat=True))  # type: ignore[attr-defined]

    context: Dict[str, Any] = {
        'title': f'Подписчики {user.username}',
        'profile_user': user,
        'followers': followers,
        'page_type': 'followers',
        'following_ids': following_ids,
    }
    return render(request, 'accounts/follow_list.html', context)


def following_view(request: HttpRequest, username: str) -> HttpResponse:
    """Список подписок пользователя"""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following')
    
    following_ids: Set[int] = set()
    if request.user.is_authenticated:
        current_user = cast(User, request.user)
        following_ids = set(current_user.following.values_list('following__id', flat=True))  # type: ignore[attr-defined]

    context: Dict[str, Any] = {
        'title': f'Подписки {user.username}',
        'profile_user': user,
        'following': following,
        'page_type': 'following',
        'following_ids': following_ids,
    }
    return render(request, 'accounts/follow_list.html', context)
