from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.URLField(default="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.twomonkeys.net%2Fblog%2F2018%2F11%2F12%2Fthe-post-im-posting-because-i-cant-post-posts&psig=AOvVaw32O_Nx5XTJiEJ5dz7GKQIc&ust=1759248213373000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCOi_pKis_o8DFQAAAAAdAAAAABAE", verbose_name="URL зображення")
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



