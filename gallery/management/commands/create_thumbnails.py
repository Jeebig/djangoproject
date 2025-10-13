from typing import Any
from django.core.management.base import BaseCommand
from django.db.models import Q
from gallery.models import Image

class Command(BaseCommand):
    help = 'Создает миниатюры для всех изображений без миниатюр'

    def handle(self, *args: Any, **options: Any) -> None:
        # Учитываем и NULL, и пустую строку
        images_without_thumbnails = Image.objects.filter(Q(thumbnail__isnull=True) | Q(thumbnail=''))
        count = images_without_thumbnails.count()
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING('Все изображения уже имеют миниатюры.')
            )
            return
        
        self.stdout.write(f'Найдено {count} изображений без миниатюр.')
        
        for i, image in enumerate(images_without_thumbnails.iterator(), 1):
            try:
                image.create_thumbnail()
                image.save(update_fields=['thumbnail'])
                self.stdout.write(f'[{i}/{count}] Создана миниатюра для: {image.title}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[{i}/{count}] Ошибка для {image.title}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Обработано {count} изображений.')
        )