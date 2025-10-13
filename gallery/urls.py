from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_index, name='gallery-index'),
    path('upload/', views.upload_image, name='upload-image'),
    path('image/<int:image_id>/', views.image_detail, name='image-detail'),
    path('image/<int:image_id>/delete/', views.delete_image, name='delete-image'),
]