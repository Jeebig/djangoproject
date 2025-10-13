from typing import Any
import io
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.files.base import ContentFile
from PIL import Image as PILImage

User = get_user_model()

# Create your models here.
class Category(models.Model):
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Auto-generate a unicode-friendly unique slug if missing.

        We allow unicode so that Cyrillic category names produce a non-empty slug.
        If the generated slug already exists (rare on direct save), append a numeric suffix.
        """
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            if not base_slug:
                base_slug = "category"
            slug_candidate = base_slug
            counter = 2
            while Category.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

class Post(models.Model):
    slug = models.SlugField(max_length=200, unique=True, db_index=True, verbose_name="URL")
    title = models.CharField(max_length=200 , verbose_name="Заголовок")
    content = models.TextField(verbose_name="Зміст")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата створення")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.URLField(default="https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=800&h=400&fit=crop&crop=center", verbose_name="URL зображення")
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True, verbose_name='Теги')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Пости"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Auto-generate unicode-friendly slug for the post title if missing.

        Ensures uniqueness by appending a numeric suffix when needed.
        """
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = "post"
            slug_candidate = base_slug
            counter = 2
            while Post.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Назва тега")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Зміст коментаря")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    is_active = models.BooleanField(default=True, verbose_name="Активний")

    def __str__(self):
        return f"Коментар від {self.author.username} до {self.post.title}"

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        ordering = ['-created_at']
    

class PostImage(models.Model):
    """Дополнительные изображения для поста (файлы, порядок и подпись)."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name="Пост")
    image = models.ImageField(upload_to='blog/posts/%Y/%m/%d/', verbose_name="Изображение")
    thumbnail = models.ImageField(upload_to='blog/posts/thumbnails/%Y/%m/%d/', blank=True, null=True, verbose_name="Миниатюра")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        verbose_name = "Изображение поста"
        verbose_name_plural = "Изображения поста"
        ordering = ['order', 'id']
        constraints = []
        indexes = [
            models.Index(fields=['post', 'order']),
        ]

    def __str__(self) -> str:
        return f"{self.post.title} — {self.image.name}"

    @property
    def url(self) -> str:
        try:
            return self.image.url
        except Exception:
            return ""

    def create_thumbnail(self, size: tuple[int, int] = (400, 400)) -> None:
        """Создает миниатюру для изображения поста и сохраняет в поле thumbnail."""
        if not self.image:
            return

        # Открываем оригинальное изображение
        img = PILImage.open(self.image)

        # Приводим к RGB, если необходимо
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        # Создаем миниатюру с сохранением пропорций
        img.thumbnail(size, PILImage.Resampling.LANCZOS)

        # Сохраняем миниатюру в память
        thumb_io = io.BytesIO()
        img.save(thumb_io, format="JPEG", quality=90)
        thumb_io.seek(0)

        # Имя файла миниатюры
        base_name = os.path.basename(self.image.name)
        thumb_name = f"thumb_{base_name}"
        thumb_name = thumb_name.replace('.png', '.jpg').replace('.webp', '.jpg')

        # Записываем в поле thumbnail (без сохранения модели)
        self.thumbnail.save(thumb_name, ContentFile(thumb_io.read()), save=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Переопределяем save для автоматического создания миниатюры один раз."""
        is_new = self.pk is None
        # Сначала сохраняем, чтобы у файла был путь
        super().save(*args, **kwargs)

        # Создаем миниатюру, если есть оригинал и нет миниатюры или файл обновили
        if self.image and (is_new or not self.thumbnail):
            self.create_thumbnail()
            super().save(update_fields=["thumbnail"]) 
