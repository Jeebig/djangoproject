from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from .models import Product
from orders.models import Order, OrderItem, ShippingAddress, Payment
from decimal import Decimal


CART_SESSION_KEY = 'cart_items'

from typing import Any, cast, TypedDict, Optional


class CartItemSummary(TypedDict):
    id: int
    qty: int
    subtotal: Decimal


class CartViewItem(TypedDict):
    product: Product
    qty: int
    subtotal: Decimal


def _get_cart(session: Any) -> dict[int, int]:
    """Return cart with int keys even if session stored strings."""
    raw = cast(dict[str, Any], session.get(CART_SESSION_KEY, {}) or {})
    try:
        return {int(k): int(v) for k, v in raw.items()}
    except Exception:
        return {}


def _save_cart(session: Any, cart: dict[int, int]):
    # store as string keys for JSON serialization
    session[CART_SESSION_KEY] = {str(k): int(v) for k, v in cart.items() if int(v) > 0}
    session.modified = True


def _cart_summary(cart: dict[int, int]) -> tuple[list[CartItemSummary], Decimal, int]:
    product_ids = list(cart.keys())
    products = Product.objects.filter(id__in=product_ids)
    items: list[CartItemSummary] = []
    total: Decimal = Decimal(0)
    count: int = 0
    for p in products:
        qty = int(cart.get(int(p.pk), 0))
        subtotal: Decimal = p.price * qty
        total += subtotal
        count += qty
        items.append({"id": int(p.pk), "qty": qty, "subtotal": subtotal})
    return items, total, count


def product_list(request: HttpRequest) -> HttpResponse:
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'shop/product_list.html', {"products": products})


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'shop/product_detail.html', {"product": product})


def cart_view(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request.session)
    product_ids = list(cart.keys())
    products = Product.objects.filter(id__in=product_ids)
    items: list[CartViewItem] = []
    total: Decimal = Decimal(0)
    for p in products:
        qty = int(cart.get(int(p.pk), 0))
        subtotal: Decimal = p.price * qty
        total += subtotal
        items.append({"product": p, "qty": qty, "subtotal": subtotal})
    return render(request, 'shop/cart.html', {"items": items, "total": total})


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    # ensure product exists
    get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request.session)
    qty = max(1, int(request.POST.get('qty', 1)))
    cart[product_id] = int(cart.get(product_id, 0)) + qty
    _save_cart(request.session, cart)
    next_url = request.POST.get('next')
    return redirect(next_url or 'shop:cart')


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = _get_cart(request.session)
    cart.pop(product_id, None)
    _save_cart(request.session, cart)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        _, total, count = _cart_summary(cart)
        return JsonResponse({"ok": True, "removed": True, "id": product_id, "total": str(total), "count": count})
    return redirect('shop:cart')


@require_POST
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    qty = int(request.POST.get('qty', 1))
    cart = _get_cart(request.session)
    if qty <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = qty
    _save_cart(request.session, cart)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        items, total, count = _cart_summary(cart)
        item: Optional[CartItemSummary] = next((i for i in items if i["id"] == product_id), None)
        return JsonResponse({
            "ok": True,
            "id": product_id,
            "qty": item["qty"] if item else 0,
            "subtotal": str(item["subtotal"]) if item else "0",
            "total": str(total),
            "count": count,
            "removed": item is None,
        })
    return redirect('shop:cart')


@require_POST
def cart_clear(request: HttpRequest) -> HttpResponse:
    _save_cart(request.session, {})
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"ok": True, "cleared": True, "total": "0", "count": 0})
    return redirect('shop:cart')


def checkout(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        cart = _get_cart(request.session)
        if not cart:
            return redirect('shop:product-list')
        email = request.POST.get('email')
        if not email and request.user.is_authenticated:
            email = getattr(request.user, 'email', '')
        order = Order.objects.create(user=request.user if request.user.is_authenticated else None, email=email)
        products = Product.objects.filter(id__in=cart.keys())
        for p in products:
            qty = int(cart.get(int(p.pk), 0))
            if qty > 0:
                OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)
        # Optional: simple shipping from posted fields (fallback to minimal data)
        full_name = request.POST.get('full_name') or (cast(Any, request.user).get_full_name() if request.user.is_authenticated else '')
        city = request.POST.get('city') or ''
        address_line1 = request.POST.get('address_line1') or ''
        address_line2 = request.POST.get('address_line2') or ''
        postal_code = request.POST.get('postal_code') or ''
        country = request.POST.get('country') or ''
        phone = request.POST.get('phone') or ''
        if city and address_line1:
            ShippingAddress.objects.create(
                order=order,
                full_name=full_name or 'Без имени',
                city=city,
                address_line1=address_line1,
                address_line2=address_line2,
                postal_code=postal_code,
                country=country,
                phone=phone,
            )
        # Create payment record (pending)
        method = request.POST.get('payment_method') or Payment.Method.COD
        Payment.objects.create(order=order, method=method, status=Payment.Status.PENDING, amount=cast(Any, order).total)
        _save_cart(request.session, {})
        # Email confirmation (dev backend may print to console)
        try:
            from django.core.mail import send_mail
            # Compose a simple text receipt
            lines = [f"{order}", "", "Состав:"]
            for oi in OrderItem.objects.filter(order=order):
                oi_any = cast(Any, oi)
                lines.append(f" - {oi_any.product.name} x{oi_any.quantity} = {oi_any.subtotal} ₴")
            lines.append("")
            total_any = cast(Any, order).total
            lines.append(f"Итого: {total_any} ₴")
            if email:
                send_mail(
                    subject=f"Ваш {order}",
                    message="\n".join(lines),
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=True,
                )
        except Exception:
            pass
        return render(request, 'shop/checkout_success.html', {"order": order})
    return render(request, 'shop/checkout.html')
