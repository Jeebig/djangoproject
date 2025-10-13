from django.core.management.base import BaseCommand
from typing import Any, Dict
from blog.models import Post, PostImage
from gallery.models import Image as GalleryImage


class Command(BaseCommand):
    help = "Seed PostImage for posts using existing public Gallery images to reach a target per-post count"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('--min', type=int, default=2, help='Minimum images per post after seeding (default: 2)')
        parser.add_argument('--limit', type=int, default=100, help='Max images to copy in total (safety)')

    def handle(self, *args: object, **options: Dict[str, Any]) -> None:
        target_min = int(options.get('min', 2))
        limit = int(options.get('limit', 100))
        copied = 0
        affected = 0

        gallery_qs = GalleryImage.objects.filter(is_public=True).order_by('-uploaded_at')
        gallery_iter = iter(gallery_qs)

        for post in Post.objects.all().prefetch_related('images'):
            current_count = post.images.count()  # type: ignore[attr-defined]
            if current_count >= target_min:
                continue
            needed = target_min - current_count
            added_here = 0
            while needed > 0 and copied < limit:
                try:
                    gimg = next(gallery_iter)
                except StopIteration:
                    break
                pimg = PostImage(post=post, order=current_count + added_here)
                pimg.image.name = gimg.image.name
                pimg.save()
                added_here += 1
                needed -= 1
                copied += 1
            if added_here:
                affected += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded from gallery. Posts affected: {affected}, images copied: {copied}"))
