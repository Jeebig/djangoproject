from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Назва категорії")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
class Post(models.Model):
    title = models.CharField(max_length=50 , verbose_name="Заголовок")
    content = models.TextField(verbose_name="Зміст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Пости"

class Tag(models.Model):
    name = models.CharField(max_length=30, verbose_name="Назва тега")

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


# Many-to-many relationship between Post and Tag
Post.add_to_class('tags', models.ManyToManyField(Tag, related_name="posts", verbose_name="Теги", blank=True))



