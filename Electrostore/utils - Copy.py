import re
import uuid
import random
from functools import wraps
from datetime import datetime
from flask import session, flash, redirect, url_for, request, abort
from flask_login import current_user
from models import db, CartItem, Product, Coupon
from config import Config

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Administrator privileges are required.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def generate_order_number():
    year = datetime.utcnow().year
    random_part = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))
    return f"VC-{year}-{random_part}"


def format_currency(value):
    try:
        val = float(value)
        return f"${val:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


def get_guest_session_id():
    if 'guest_session_id' not in session:
        session['guest_session_id'] = str(uuid.uuid4())
    return session['guest_session_id']


def get_cart_items_and_totals(user=None, session_id=None, coupon_code=None):
    if user and user.is_authenticated:
        items = CartItem.query.filter_by(user_id=user.id).all()
    elif session_id:
        items = CartItem.query.filter_by(session_id=session_id).all()
    else:
        items = []

    subtotal = sum(item.subtotal for item in items)
    item_count = sum(item.quantity for item in items)

    # Shipping calculation
    if subtotal == 0:
        shipping_fee = 0.0
    elif subtotal >= Config.FREE_SHIPPING_THRESHOLD:
        shipping_fee = 0.0
    else:
        shipping_fee = Config.STANDARD_SHIPPING_FEE

    # Coupon discount calculation
    discount_amount = 0.0
    applied_coupon = None
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code.strip().upper()).first()
        if coupon:
            is_valid, msg = coupon.is_valid(subtotal)
            if is_valid:
                discount_amount = coupon.calculate_discount(subtotal)
                applied_coupon = coupon

    # Tax calculation (applied on discounted subtotal)
    taxable_amount = max(0.0, subtotal - discount_amount)
    tax_amount = round(taxable_amount * Config.TAX_RATE, 2)

    total_amount = round(max(0.0, subtotal - discount_amount + shipping_fee + tax_amount), 2)

    return {
        'items': items,
        'cart_items': items,
        'item_count': item_count,
        'subtotal': round(subtotal, 2),
        'shipping_fee': round(shipping_fee, 2),
        'discount_amount': round(discount_amount, 2),
        'tax_amount': round(tax_amount, 2),
        'total_amount': total_amount,
        'applied_coupon': applied_coupon,
        'free_shipping_threshold': Config.FREE_SHIPPING_THRESHOLD,
        'free_shipping_needed': max(0.0, round(Config.FREE_SHIPPING_THRESHOLD - subtotal, 2))
    }


def sync_guest_cart_to_user(session_id, user_id):
    if not session_id or not user_id:
        return
    guest_items = CartItem.query.filter_by(session_id=session_id).all()
    for g_item in guest_items:
        existing_user_item = CartItem.query.filter_by(user_id=user_id, product_id=g_item.product_id).first()
        if existing_user_item:
            existing_user_item.quantity += g_item.quantity
            db.session.delete(g_item)
        else:
            g_item.user_id = user_id
            g_item.session_id = None
    db.session.commit()