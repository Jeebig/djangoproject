from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Кастомная модель пользователя"""
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    avatar = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Аватар", 
        default="https://www.gravatar.com/avatar/?d=mp"
    )
    
    def get_followers_count(self):
        """Количество подписчиков"""
        return self.followers.count()
    
    def get_following_count(self):
        """Количество подписок"""
        return self.following.count()
    
    def is_following(self, user):
        """Проверяет, подписан ли текущий пользователь на другого"""
        return self.following.filter(following=user).exists()
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Follow(models.Model):
    """Модель подписок между пользователями"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        verbose_name="Подписчик"
    )
    following = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers',
        verbose_name="На кого подписан"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('follower', 'following')
        
    def __str__(self):
        return f"{self.follower.username} подписан на {self.following.username}"


class Notification(models.Model):
    """Простая система уведомлений для пользователей"""
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Получатель',
    )
    message = models.CharField(max_length=255, verbose_name='Сообщение')
    # Необязательная ссылка для перехода (например, на профиль подписчика)
    link = models.CharField(max_length=255, blank=True, default='', verbose_name='Ссылка')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Создано')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self) -> str:
        return f"{self.recipient.username}: {self.message}"

