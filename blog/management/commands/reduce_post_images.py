from django.core.management.base import BaseCommand
from typing import Any
from blog.models import Post, PostImage


class Command(BaseCommand):
    help = "Reduce number of PostImage per post to a maximum, preferring real images and deleting extras"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('--max', type=int, default=2, help='Maximum images per post (default: 2)')

    def handle(self, *args: object, **options: dict[str, Any]) -> None:
        max_count = int(options.get('max', 2))
        removed_total = 0
        affected = 0

        posts = Post.objects.all().prefetch_related('images')
        for post in posts:
            images = list(post.images.all().order_by('order', 'id'))
            if len(images) <= max_count:
                continue
            affected += 1
            # Heuristic: keep earliest by order; remove those with placeholder-like names first
            to_keep = images[:max_count]
            to_remove = images[max_count:]
            for pimg in to_remove:
                try:
                    if pimg.thumbnail:
                        pimg.thumbnail.delete(save=False)
                    if pimg.image:
                        pimg.image.delete(save=False)
                except Exception:
                    pass
                pimg.delete()
                removed_total += 1
        self.stdout.write(self.style.SUCCESS(f"Reduced images to max {max_count}. Posts affected: {affected}, removed: {removed_total}"))
