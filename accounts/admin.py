from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

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
    
    # Поля при создании нового пользователя
    add_fieldsets = list(UserAdmin.add_fieldsets) + [
        ('Дополнительная информация', {
            'fields': ('email', 'phone', 'city', 'birth_date', 'avatar')
        }),
    ]
