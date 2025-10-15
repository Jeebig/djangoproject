from io import BytesIO
from typing import Tuple
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image as PILImage

from blog.models import Post, PostImage


class Command(BaseCommand):
    help = "Seed 1-3 generated images for posts without PostImage entries"

    def handle(self, *args: object, **options: object) -> None:
        colors: Tuple[Tuple[int, int, int], ...] = (
            (220, 53, 69),
            (25, 135, 84),
            (13, 110, 253),
        )
        total_posts = 0
        total_images = 0

        posts = Post.objects.all().prefetch_related('images')
        for post in posts:
            if post.images.exists():
                continue
            total_posts += 1
            # Generate 2 images for visibility
            for idx, color in enumerate(colors[:2], start=1):
                img = PILImage.new("RGB", (1024, 576), color)
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=90)
                buf.seek(0)
                content = ContentFile(buf.read(), name=f"auto_{post.id}_{idx}.jpg")

                pimg = PostImage(post=post, order=idx - 1)
                pimg.image.save(content.name, content, save=True)
                total_images += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded images: {total_images} for posts: {total_posts}"))
