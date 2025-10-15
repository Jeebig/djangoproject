from io import BytesIO
from typing import Tuple
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image as PILImage

from blog.models import Post, PostImage


class Command(BaseCommand):
    help = "Ensure every post has at least 3 images by generating missing ones"

    def add_arguments(self, parser) -> None:
        parser.add_argument('--min', type=int, default=3, help='Minimum images per post')

    def handle(self, *args: object, **options: object) -> None:
        target: int = int(options.get('min', 3))
        colors: Tuple[Tuple[int, int, int], ...] = (
            (220, 53, 69),
            (25, 135, 84),
            (13, 110, 253),
            (255, 193, 7),
            (111, 66, 193),
        )
        total_posts = 0
        total_added = 0

        posts = Post.objects.all().prefetch_related('images')
        for post in posts:
            current = list(post.images.all().order_by('order', 'id'))
            if len(current) >= target:
                continue
            total_posts += 1
            # continue order after existing
            next_order = current[-1].order + 1 if current else 0
            missing = target - len(current)
            for i in range(missing):
                color = colors[(len(current) + i) % len(colors)]
                img = PILImage.new("RGB", (1280, 720), color)
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=88)
                buf.seek(0)
                content = ContentFile(buf.read(), name=f"topup_{post.pk}_{next_order}.jpg")
                pimg = PostImage(post=post, order=next_order)
                pimg.image.save(content.name, content, save=True)  # triggers thumbnail
                next_order += 1
                total_added += 1

        self.stdout.write(self.style.SUCCESS(f"Top-up complete. Posts affected: {total_posts}, images added: {total_added}"))
