from io import BytesIO
from typing import Tuple
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image as PILImage

from blog.models import Category, Post, PostImage


class Command(BaseCommand):
    help = "Seed a demo post with generated images to test thumbnails"

    def handle(self, *args: object, **options: object) -> None:
        User = get_user_model()

        # Ensure author exists
        author = User.objects.first()
        if not author:
            author = User.objects.create_user(username="demo", password="demo12345")
            self.stdout.write(self.style.WARNING("Created demo user 'demo' with password 'demo12345'"))

        # Ensure category exists
        category, _ = Category.objects.get_or_create(
            slug="demo", defaults={"name": "Demo"}
        )

        # Create or get a demo post
        title = "Demo Thumbnails"
        post, created = Post.objects.get_or_create(
            slug=slugify(title, allow_unicode=True),
            defaults={
                "title": title,
                "content": "This is a demo post with generated images to test thumbnails.",
                "category": category,
                "author": author,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created post: {post.title}"))
        else:
            self.stdout.write(self.style.WARNING(f"Using existing post: {post.title}"))

        # Generate a few images in memory
        colors: Tuple[Tuple[int, int, int], ...] = (
            (220, 53, 69),   # red-ish
            (25, 135, 84),   # green-ish
            (13, 110, 253),  # blue-ish
        )
        created_cnt = 0
        for idx, color in enumerate(colors, start=1):
            img = PILImage.new("RGB", (1024, 576), color)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            content = ContentFile(buf.read(), name=f"demo_{idx}.jpg")

            # Order after existing
            order = post.images.count()
            pimg = PostImage(post=post, order=order)
            pimg.image.save(content.name, content, save=True)  # triggers thumbnail via model save()
            created_cnt += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_cnt} demo images for post '{post.title}'"))
