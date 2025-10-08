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
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

