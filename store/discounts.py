from decimal import Decimal

def calculate_discounts(user, order_items):
    total = sum(item['product'].price * item['quantity'] for item in order_items)
    discounts = {}
    final_total = total

    # Percentage Discount
    if total > 5000:
        discount = total * Decimal('0.10')
        discounts['percentage_discount'] = float(discount)
        final_total -= discount

    # Flat Discount
    if user.order_set.count() > 5:
        discount = Decimal('500.00')
        discounts['flat_discount'] = float(discount)
        final_total -= discount

    # Category-Based Discount
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

    return final_total, discounts
