from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from shop.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("Новый")
        PAID = "paid", _("Оплачен")
        SHIPPED = "shipped", _("Отправлен")
        COMPLETED = "completed", _("Завершен")
        CANCELED = "canceled", _("Отменен")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Пользователь"))
    email = models.EmailField(verbose_name=_("Email"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name=_("Статус"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлен"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self) -> str:
        return f"Заказ #{self.pk}"

    @property
    def total(self) -> Decimal:
        items = getattr(self, 'items', None)
        iterable: list[object]
        if items is not None:
            iterable = list(items.all())  # force to list for stable typing
        else:
            iterable = []
        total = Decimal(0)
        for it in iterable:
            subtotal = getattr(it, 'subtotal', Decimal(0))
            total += subtotal  # type: ignore[operator]
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказа")

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, related_name="shipping", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = _("Адрес доставки")
        verbose_name_plural = _("Адреса доставки")

    def __str__(self) -> str:
        return f"{self.full_name}, {self.city}"


class Payment(models.Model):
    class Method(models.TextChoices):
        COD = "cod", _("Наложенный платеж")
        CARD = "card", _("Карта")

    class Status(models.TextChoices):
        PENDING = "pending", _("Ожидает")
        PAID = "paid", _("Оплачено")
        FAILED = "failed", _("Неуспешно")

    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.COD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Платеж")
        verbose_name_plural = _("Платежи")

    def __str__(self) -> str:
        return f"Payment #{self.pk} ({self.status})"
