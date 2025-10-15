from django.core.management.base import BaseCommand
from shop.models import Product


class Command(BaseCommand):
    help = "Создать (или пересоздать) миниатюры для товаров"

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Пересоздавать даже если миниатюра уже есть')

    def handle(self, *args, **options):
        force = options.get('force', False)
        count = 0
        for p in Product.objects.all():
            if p.image and (force or not p.thumbnail):
                p.create_thumbnail()
                p.save(update_fields=['thumbnail'])
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Миниатюр создано/обновлено: {count}"))
