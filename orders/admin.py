from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, Payment


class OrderItemInline(admin.TabularInline):  # type: ignore[type-arg]
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("order", "full_name", "city")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("order", "method", "status", "amount")
