from decimal import Decimal
from django.core.cache import cache
from django.conf import settings
import hashlib
import json

def generate_cache_key(user_id, items):
    """Generate a unique cache key based on user and item data"""
    raw = json.dumps({
        "user_id": user_id,
        "items": [
            {"product_id": i['product'].id, "quantity": i['quantity']}
            for i in items
        ]
    }, sort_keys=True)
    return "discounts:" + hashlib.md5(raw.encode()).hexdigest()

def calculate_discounts(user, order_items):
    cache_key = generate_cache_key(user.id, order_items)
    cached_result = cache.get(cache_key)

    if cached_result:
        # print("🟢 Redis Cache Hit")
        return cached_result['final_total'], cached_result['discounts']

    total = sum(item['product'].price * item['quantity'] for item in order_items)
    discounts = {}
    final_total = total

    # Rule 1: Percentage Discount
    if total > 5000:
        discount = total * Decimal('0.10')
        discounts['percentage_discount'] = float(discount)
        final_total -= discount

    # Rule 2: Flat Discount if user has more than 5 orders
    if user.order_set.count() > 5:
        discount = Decimal('500.00')
        discounts['flat_discount'] = float(discount)
        final_total -= discount

    # Rule 3: Category Discount (Electronics)
    electronics_total = sum(
        item['product'].price * item['quantity']
        for item in order_items
        if item['product'].category.name.lower() == 'electronics'
    )
    electronics_quantity = sum(
        item['quantity']
        for item in order_items
        if item['product'].category.name.lower() == 'electronics'
    )
    if electronics_quantity > 3:
        discount = electronics_total * Decimal('0.05')
        discounts['category_discount'] = float(discount)
        final_total -= discount
    # print("🔵 Redis Cache Miss (Calculating Fresh)")
    # Cache the result
    cache.set(cache_key, {'final_total': final_total, 'discounts': discounts}, timeout=settings.CACHE_TTL)

    return final_total, discounts
