from __future__ import annotations

import os
import posixpath
import urllib.parse
import urllib.request
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from blog.models import Post, PostImage


def _filename_from_url(url: str, fallback: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = posixpath.basename(parsed.path)
    if not name:
        return fallback
    return name


class Command(BaseCommand):
    help = "Download legacy Post.image URL into PostImage and (optionally) remove seeded placeholders"

    def add_arguments(self, parser) -> None:
        parser.add_argument('--cleanup-seeded', action='store_true', default=True,
                            help='Remove previously seeded placeholder images (auto_/topup_) for affected posts')
        parser.add_argument('--skip-cleanup', action='store_true', default=False,
                            help='Do not remove seeded placeholder images')

    def handle(self, *args: object, **options: object) -> None:
        cleanup_seeded: bool = bool(options.get('cleanup_seeded', True)) and not bool(options.get('skip_cleanup', False))

        posts = Post.objects.exclude(image__isnull=True).exclude(image__exact='')
        imported = 0
        cleaned = 0

        for post in posts:
            url = post.image
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:  # nosec - controlled by admin content
                    data = resp.read()
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to download for post #{post.pk}: {e}"))
                continue

            base_name = _filename_from_url(url, fallback=f"legacy_{post.pk}.jpg")
            content = ContentFile(data, name=base_name)

            # If a legacy image already exists as PostImage (by name), skip create
            exists = post.images.filter(image__icontains=base_name).exists()
            if not exists:
                order0_exists = post.images.filter(order=0).exists()
                order = 0 if not order0_exists else 0  # keep 0, but others will be after
                pimg = PostImage(post=post, order=order)
                pimg.image.save(base_name, content, save=True)
                imported += 1

                # shift others' order if needed to keep legacy first
                if order0_exists:
                    for other in post.images.exclude(pk=pimg.pk).order_by('order', 'id'):
                        other.order += 1
                        other.save(update_fields=['order'])

            if cleanup_seeded:
                # remove seeded placeholders created by previous commands
                seeded = post.images.filter(image__regex=r'.*/(auto_|topup_)').all()
                for s in seeded:
                    try:
                        if s.thumbnail:
                            s.thumbnail.delete(save=False)
                        if s.image:
                            s.image.delete(save=False)
                    except Exception:
                        pass
                    s.delete()
                    cleaned += 1

        self.stdout.write(self.style.SUCCESS(f"Imported: {imported} legacy images; cleaned placeholders: {cleaned}"))
