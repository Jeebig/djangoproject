from __future__ import annotations

import csv
import posixpath
import urllib.parse
import urllib.request
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from typing import Any, Dict, List

from blog.models import Post, PostImage


def _filename_from_url(url: str, fallback: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = posixpath.basename(parsed.path)
    return name or fallback


class Command(BaseCommand):
    help = "Import images for posts from a CSV file (slug,url). Only applies to posts without post.image."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('csv_path', type=str, help='Path to CSV file with columns: slug,url')
        parser.add_argument('--set-legacy', action='store_true', default=False,
                            help='Also set Post.image to the first URL for that post')

    def handle(self, *args: object, **options: Dict[str, Any]) -> None:
        csv_path: str = str(options.get('csv_path'))
        set_legacy: bool = bool(options.get('set_legacy', False))

        try:
            fh = open(csv_path, 'r', encoding='utf-8')
        except OSError as e:
            raise CommandError(f"Cannot open CSV: {e}")

        reader = csv.DictReader(fh)
        required = {'slug', 'url'}
        if not required.issubset(reader.fieldnames or {}):
            raise CommandError('CSV must have columns: slug,url')

        created = 0
        updated_legacy = 0
        grouped: Dict[str, List[str]] = {}
        for row in reader:
            slug = (row.get('slug') or '').strip()
            url = (row.get('url') or '').strip()
            if not slug or not url:
                continue
            grouped.setdefault(slug, []).append(url)

        for slug, urls in grouped.items():
            try:
                post = Post.objects.get(slug=slug)
            except Post.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"Post not found for slug: {slug}"))
                continue

            # Only apply to posts without legacy post.image
            if post.image:
                continue

            order = post.images.count()  # type: ignore[attr-defined]
            for i, url in enumerate(urls):
                try:
                    with urllib.request.urlopen(url, timeout=15) as resp:  # nosec - admin-provided list
                        data = resp.read()
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Download failed for {slug}: {e}"))
                    continue
                name = _filename_from_url(url, f"csv_{slug}_{i}.jpg")
                content = ContentFile(data, name=name)
                pimg = PostImage(post=post, order=int(order))
                pimg.image.save(name, content, save=True)
                order += 1
                created += 1

            if set_legacy and urls:
                post.image = urls[0]
                post.save(update_fields=['image'])
                updated_legacy += 1

        fh.close()
        self.stdout.write(self.style.SUCCESS(f"Imported images: {created}; Posts legacy set: {updated_legacy}"))
