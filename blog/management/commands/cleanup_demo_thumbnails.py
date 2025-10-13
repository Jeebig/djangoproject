from django.core.management.base import BaseCommand
from django.utils.text import slugify
from blog.models import Post, PostImage


class Command(BaseCommand):
    help = "Remove demo post images and thumbnails (post slug 'demo-thumbnails')"

    def handle(self, *args: object, **options: object) -> None:
        slug = slugify("Demo Thumbnails", allow_unicode=True)
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            self.stdout.write(self.style.WARNING("Demo post not found, nothing to cleanup."))
            return

        images = list(PostImage.objects.filter(post=post))
        if not images:
            self.stdout.write(self.style.WARNING("No PostImage records for demo post."))
            return

        removed = 0
        for pimg in images:
            # Delete files from storage, then the record
            try:
                if pimg.thumbnail:
                    pimg.thumbnail.delete(save=False)
                if pimg.image:
                    pimg.image.delete(save=False)
            except Exception:
                pass
            pimg.delete()
            removed += 1

        self.stdout.write(self.style.SUCCESS(f"Removed {removed} demo images and thumbnails."))
