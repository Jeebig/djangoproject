from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма регистрации пользователя с дополнительными полями"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        }),
        help_text='Обязательное поле. Введите действующий email адрес.'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+38 (xxx) xxx-xx-xx'
        }),
        help_text='Необязательно. Формат: +38 (xxx) xxx-xx-xx'
    )
    
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш город'
        })
    )
    
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Необязательно. Дата рождения'
    )
    
    avatar = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/avatar.jpg'
        }),
        help_text='Необязательно. Ссылка на ваш аватар'
    )
    
    class Meta:
        model = User
        fields = (
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'phone', 
            'city', 
            'birth_date', 
            'avatar',
            'password1', 
            'password2'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Стилизация стандартных полей
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
        
        # Обновление меток на русском языке
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Email'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Телефон'
        self.fields['city'].label = 'Город'
        self.fields['birth_date'].label = 'Дата рождения'
        self.fields['avatar'].label = 'Аватар'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Добавляем help_text для username
        self.fields['username'].help_text = 'Обязательно. 150 символов или меньше. Только буквы, цифры и символы @/./+/-/_.'
    
    def clean_email(self):
        """Проверяем уникальность email"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email
    
    def save(self, commit=True):
        """Сохраняем пользователя с дополнительными полями"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.city = self.cleaned_data['city']
        user.birth_date = self.cleaned_data['birth_date']
        user.avatar = self.cleaned_data['avatar']
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Кастомная форма входа с Bootstrap стилями"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'