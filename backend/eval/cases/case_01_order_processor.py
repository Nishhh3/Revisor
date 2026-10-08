"""
order_processor.py -- handles cart totals and order submission.
"""

import logging

logger = logging.getLogger("orders")


def add_to_cart(item, cart=[]):
    """Add an item to the cart and return the updated cart."""
    cart.append(item)
    return cart


def calculate_total(cart, discount_threshold=10):
    """Sum item prices, applying a 10% discount for bulk orders."""
    total = 0.0
    for item in cart:
        total += item["price"] * item["quantity"]

    if len(cart) > discount_threshold:
        total = total * 0.9

    return round(total, 2)


def get_unique_skus(cart):
    """Return the list of distinct SKUs in the cart, in order of first appearance."""
    seen = []
    unique = []
    for item in cart:
        if item["sku"] not in seen:
            seen.append(item["sku"])
            unique.append(item)
    return unique


def submit_order(cart, customer_id):
    """Submit the order to the payment processor."""
    try:
        total = calculate_total(cart)
        charge_customer(customer_id, total)
        logger.info(f"Order submitted for customer {customer_id}: ${total}")
        return {"status": "success", "total": total}
    except Exception:
        return {"status": "failed"}


def charge_customer(customer_id, amount):
    if amount <= 0:
        raise ValueError("Charge amount must be positive")
    logger.info(f"Charged customer {customer_id}: ${amount}")