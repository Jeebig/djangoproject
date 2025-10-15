from django.contrib import admin
from django.utils.html import format_html
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """Админка для изображений"""
    list_display = ['title', 'thumbnail_preview', 'uploaded_by', 'uploaded_at', 'is_public']
    list_filter = ['is_public', 'uploaded_at', 'uploaded_by']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at', 'thumbnail_preview']
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image', 'thumbnail_preview')
        }),
        ('Настройки', {
            'fields': ('is_public', 'uploaded_by', 'uploaded_at')
        }),
    )
    
    @admin.display(description="Превью")
    def thumbnail_preview(self, obj: Image) -> str:
        """Показывает превью миниатюры в админке"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.thumbnail.url
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "Нет изображения"
    

