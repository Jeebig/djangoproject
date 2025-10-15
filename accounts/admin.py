from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для кастомной модели User"""
    
    # Поля для отображения в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'city', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'city', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    
    # Поля для редактирования пользователя
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Дополнительная информация', {
            'fields': ('phone', 'city', 'birth_date', 'avatar')
        }),
    ]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-панель для подписок"""
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    raw_id_fields = ('follower', 'following')
    date_hierarchy = 'created_at'
    
    # Поля при создании нового пользователя
    add_fieldsets = list(UserAdmin.add_fieldsets) + [
        ('Дополнительная информация', {
            'fields': ('email', 'phone', 'city', 'birth_date', 'avatar')
        }),
    ]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    raw_id_fields = ('recipient',)
    date_hierarchy = 'created_at'
