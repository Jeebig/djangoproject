from typing import Any
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image as PILImage
from django.core.files.base import ContentFile
import io
import os

User = get_user_model()

class Image(models.Model):
    """Модель для изображений в галерее"""
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='gallery/%Y/%m/%d/', verbose_name="Изображение")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Загружено пользователем")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    is_public = models.BooleanField(default=True, verbose_name="Публичное")
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/%Y/%m/%d/', blank=True, null=True, verbose_name="Миниатюра")
    
    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('gallery:image-detail', kwargs={'image_id': self.pk})
    
    def create_thumbnail(self, size: tuple[int, int] = (300, 300)) -> None:
        """Создает миниатюру изображения"""
        if not self.image:
            return
        
        # Открываем оригинальное изображение
        img = PILImage.open(self.image.path)
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Создаем миниатюру с сохранением пропорций
        img.thumbnail(size, PILImage.Resampling.LANCZOS)
        
        # Сохраняем в память
        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG', quality=90)
        thumb_io.seek(0)
        
        # Создаем имя файла для миниатюры
        thumb_name = f"thumb_{os.path.basename(self.image.name)}"
        thumb_name = thumb_name.replace('.png', '.jpg').replace('.webp', '.jpg')
        
        # Сохраняем миниатюру
        self.thumbnail.save(
            thumb_name,
            ContentFile(thumb_io.read()),
            save=False
        )
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Переопределяем save для автоматического создания миниатюры"""
        super().save(*args, **kwargs)
        
        # Создаем миниатюру только если она еще не создана
        if self.image and not self.thumbnail:
            self.create_thumbnail()
            # Сохраняем еще раз с миниатюрой
            super().save(update_fields=['thumbnail'])
