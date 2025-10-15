from typing import Dict, Any

CART_SESSION_KEY = 'cart_items'


def cart_context(request) -> Dict[str, Any]:
    cart = request.session.get(CART_SESSION_KEY, {}) or {}
    try:
        count = sum(int(qty) for qty in cart.values())
    except Exception:
        count = 0
    return {
        'cart_item_count': count,
    }
