from django.db import models
import io
import os
from django.core.files.base import ContentFile
from PIL import Image as PILImage
from typing import Any


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='shop/products/%Y/%m/%d/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='shop/products/thumbnails/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name

    def create_thumbnail(self, size: tuple[int, int] = (300, 300)) -> None:
        if not self.image:
            return
        img = PILImage.open(self.image)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.thumbnail(size, PILImage.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        buf.seek(0)
        base = os.path.basename(self.image.name)
        name = f"thumb_{base}".replace('.png', '.jpg').replace('.webp', '.jpg')
        self.thumbnail.save(name, ContentFile(buf.read()), save=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if self.image and (is_new or not self.thumbnail):
            self.create_thumbnail()
            super().save(update_fields=["thumbnail"])  

 
