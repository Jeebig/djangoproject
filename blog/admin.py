from django.contrib import admin

# Register your models here.
from .models import Post, Category, Tag, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): # type: ignore
    list_display = ['name']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin): # type: ignore
    list_display = ['name']
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin): # type: ignore
    list_display = ['title', 'author', 'category', 'created_at']
    list_filter = ['category', 'created_at', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin): # type: ignore
    list_display = ['post', 'author', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at']
