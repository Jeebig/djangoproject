from django.core.management.base import BaseCommand
from django.db.models import Q
from blog.models import PostImage


class Command(BaseCommand):
    help = "Create thumbnails for PostImage entries lacking them"

    def handle(self, *args: object, **options: object) -> None:
        qs = PostImage.objects.filter(Q(thumbnail__isnull=True) | Q(thumbnail__exact="")).iterator()
        created = 0
        for pimg in qs:
            if pimg.image and not pimg.thumbnail:
                try:
                    pimg.create_thumbnail()
                    pimg.save(update_fields=["thumbnail"])
                    created += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed thumbnail for #{pimg.pk}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"Created {created} post thumbnails"))
