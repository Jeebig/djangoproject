from django.db import models
from django.contrib.auth.models import AbstractUser

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

