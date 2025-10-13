from django.contrib import admin

# Register your models here.
from .models import Post, Category, Tag, Comment, PostImage
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ['name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

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

class PostImageInline(admin.TabularInline): # type: ignore
    model = PostImage
    extra = 1
    fields = ('preview', 'image', 'caption', 'order')
    readonly_fields = ('preview',)
    ordering = ('order',)

    @admin.display(description="Предпросмотр")
    def preview(self, obj: PostImage) -> str:
        if not obj:
            return ''
        # Предпочитаем миниатюру, если она есть
        if getattr(obj, 'thumbnail', None):
            try:
                return format_html('<img src="{}" style="height:64px;object-fit:cover;" />', obj.thumbnail.url)
            except Exception:
                pass
        if getattr(obj, 'image', None):
            try:
                return format_html('<img src="{}" style="height:64px;object-fit:cover;" />', obj.image.url)
            except Exception:
                return ''
        return ''

PostAdmin.inlines = [PostImageInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin): # type: ignore
    list_display = ['post', 'author', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at']