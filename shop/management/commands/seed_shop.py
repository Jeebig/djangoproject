from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from shop.models import Product
from django.utils.text import slugify
from typing import Any, List
import os
import glob

DEMO = [
    ("Футболка Python", "Удобная футболка с логотипом Python.", 499.00),
    ("Кружка Django", "Керамическая кружка с логотипом Django.", 299.00),
    ("Стикеры Dev", "Набор стикеров для ноутбука.", 149.00),
    ("Эко-сумка Coder", "Хлопковая сумка для разработчиков.", 399.00),
]


class Command(BaseCommand):
    help = "Засев демо-товаров в магазин"

    def handle(self, *args: Any, **options: Any) -> None:
        created = 0
        # Собираем изображения из uploads/gallery/** для демонстрации
        gallery_dir = os.path.join(settings.MEDIA_ROOT, 'gallery')
        patterns = [
            os.path.join(gallery_dir, '**', '*.jpg'),
            os.path.join(gallery_dir, '**', '*.jpeg'),
            os.path.join(gallery_dir, '**', '*.png'),
            os.path.join(gallery_dir, '**', '*.webp'),
        ]
        image_paths: List[str] = []
        for pat in patterns:
            image_paths.extend(glob.glob(pat, recursive=True))

        img_count = len(image_paths)
        if not img_count:
            self.stdout.write(self.style.WARNING('Изображения в uploads/gallery не найдены. Будут созданы товары без фото.'))

        for idx, (name, desc, price) in enumerate(DEMO):
            slug = slugify(name)
            obj, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'price': price,
                    'is_active': True,
                }
            )
            if was_created:
                created += 1

            # Прикрепляем изображение, если найдено, и создаём миниатюру через save()
            if img_count and not obj.image:
                img_path = image_paths[idx % img_count]
                try:
                    with open(img_path, 'rb') as fh:
                        obj.image.save(os.path.basename(img_path), File(fh), save=False)
                    # Удалим текущую миниатюру (если была), чтобы пересоздать
                    if obj.thumbnail:
                        obj.thumbnail.delete(save=False)
                    obj.save()  # type: ignore[misc]  # вызовет авто-генерацию миниатюры в модели
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Не удалось прикрепить изображение {img_path}: {e}'))

        self.stdout.write(self.style.SUCCESS(f"Создано товаров: {created}. Обработано изображений: {min(len(DEMO), img_count)}"))
