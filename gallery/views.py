from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .models import Image
from .forms import ImageUploadForm

def gallery_index(request: HttpRequest) -> HttpResponse:
    """Главная страница галереи"""
    images = Image.objects.filter(is_public=True).order_by('-uploaded_at')
    
    context = {
        'title': 'Галерея изображений',
        'images': images,
    }
    return render(request, 'gallery/gallery_index.html', context)

@login_required
def upload_image(request: HttpRequest) -> HttpResponse:
    """Загрузка изображения"""
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.uploaded_by = request.user
            image.save()
            messages.success(request, 'Изображение успешно загружено!')
            return redirect('gallery:image-detail', image_id=image.pk)
    else:
        form = ImageUploadForm()
    
    context = {
        'title': 'Загрузить изображение',
        'form': form,
    }
    return render(request, 'gallery/upload_image.html', context)

def image_detail(request: HttpRequest, image_id: int) -> HttpResponse:
    """Детальный просмотр изображения"""
    image = get_object_or_404(Image, pk=image_id)
    
    # Проверяем права доступа
    if not image.is_public and image.uploaded_by != request.user:
        messages.error(request, 'У вас нет доступа к этому изображению!')
        return redirect('gallery:gallery-index')
    
    context = {
        'title': image.title,
        'image': image,
    }
    return render(request, 'gallery/image_detail.html', context)

@login_required
def delete_image(request: HttpRequest, image_id: int) -> HttpResponse:
    """Удаление изображения"""
    image = get_object_or_404(Image, pk=image_id)
    
    # Проверяем права на удаление
    if image.uploaded_by != request.user:
        messages.error(request, 'Вы можете удалять только свои изображения!')
        return redirect('gallery:image-detail', image_id=image.pk)
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Изображение удалено!')
        return redirect('gallery:gallery-index')
    
    context = {
        'title': f'Удалить {image.title}',
        'image': image,
    }
    return render(request, 'gallery/delete_image.html', context)
