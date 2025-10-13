from django.core.management.base import BaseCommand
from typing import Any
from blog.models import Post


class Command(BaseCommand):
    help = "Audit posts for presence of Post.image and PostImage records"

    def handle(self, *args: object, **options: dict[str, Any]) -> None:
        total = Post.objects.count()
        with_legacy = Post.objects.exclude(image__isnull=True).exclude(image__exact='').count()
        with_files = 0
        missing_all = 0
        samples_missing: list[str] = []

        for p in Post.objects.all().prefetch_related('images'):
            has_files = p.images.exists()  # type: ignore[attr-defined]
            if has_files:
                with_files += 1
            if not has_files and not p.image:
                missing_all += 1
                if len(samples_missing) < 10:
                    samples_missing.append(f"{p.pk}:{p.slug}")

        self.stdout.write(self.style.SUCCESS(
            f"Total: {total}; with legacy URL: {with_legacy}; with file images: {with_files}; missing all: {missing_all}"
        ))
        if samples_missing:
            self.stdout.write("Missing examples: " + ", ".join(samples_missing))
