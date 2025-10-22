from typing import Any
from io import BytesIO
import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from PIL import Image as PILImage

from gallery.models import Image as GalleryImage


class Command(BaseCommand):
	help = "Наполнить галерею демонстрационными изображениями, созданными на лету"

	def add_arguments(self, parser) -> None:  # type: ignore[override]
		parser.add_argument(
			"--count",
			type=int,
			default=12,
			help="Сколько изображений создать (по умолчанию 12)",
		)

	def handle(self, *args: Any, **options: Any) -> None:
		User = get_user_model()

		# 1) Автор для изображений
		user = User.objects.first()
		if not user:
			user = User.objects.create_user(username="demo", password="demo12345")
			self.stdout.write(self.style.WARNING("Создан пользователь 'demo' с паролем 'demo12345'"))

		count: int = int(options.get("count") or 12)
		created = 0

		# 2) Генерируем простые цветные JPEG в памяти
		for i in range(1, count + 1):
			# Случайный приятный цвет
			color = tuple(random.randint(40, 200) for _ in range(3))

			img = PILImage.new("RGB", (1600, 900), color=color)

			buf = BytesIO()
			img.save(buf, format="JPEG", quality=90)
			buf.seek(0)

			content = ContentFile(buf.read(), name=f"gallery_demo_{i}.jpg")

			obj = GalleryImage(
				title=f"Demo #{i}",
				description="Демонстрационное изображение, созданное сидером",
				uploaded_by=user,
				is_public=True,
			)

			# save=True чтобы сразу сработало создание thumbnail в модели
			obj.image.save(content.name, content, save=True)
			created += 1

		self.stdout.write(self.style.SUCCESS(f"Создано изображений в галерее: {created}"))

