from django import forms
from .models import Image

class ImageUploadForm(forms.ModelForm):
    """Форма для загрузки изображений"""
    
    class Meta:
        model = Image
        fields = ['title', 'description', 'image', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название изображения'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание изображения (необязательно)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }