import os
import json
from datetime import datetime
from flask import (
    Flask, render_template, redirect, url_for, flash, request,
    session, jsonify, abort
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from sqlalchemy import or_, desc, asc

from config import Config
from models import (
    db, User, Category, Product, ProductImage, CartItem,
    WishlistItem, Order, OrderItem, Review, Coupon
)
from forms import (
    LoginForm, RegisterForm, ProfileForm, PasswordChangeForm,
    CheckoutForm, ReviewForm, ProductForm, CategoryForm, CouponForm
)
from utils import (
    admin_required, generate_order_number, format_currency,
    slugify, get_guest_session_id, get_cart_items_and_totals,
    sync_guest_cart_to_user
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.template_filter('currency')
def currency_filter(value):
    return format_currency(value)

@app.context_processor
def inject_global_context():
    categories = Category.query.order_by(Category.name.asc()).all()
    guest_id = session.get('guest_session_id')
    coupon_code = session.get('applied_coupon')
    cart_data = get_cart_items_and_totals(
        user=current_user if current_user.is_authenticated else None,
        session_id=guest_id,
        coupon_code=coupon_code
    )
    wishlist_count = 0
    if current_user.is_authenticated:
        wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()

    return {
        'nav_categories': categories,
        'global_cart_count': cart_data['item_count'],
        'global_cart_total': cart_data['total_amount'],
        'global_cart_subtotal': cart_data['subtotal'],
        'global_wishlist_count': wishlist_count,
        'config': Config,
        'current_year': datetime.utcnow().year
    }

# ==========================================
# STOREFRONT & CATALOG ROUTES
# ==========================================

@app.route('/')
def index():
    featured_products = Product.query.filter_by(is_featured=True).limit(8).all()
    trending_products = Product.query.filter_by(is_trending=True).limit(8).all()
    sale_products = Product.query.filter_by(is_on_sale=True).limit(4).all()
    categories = Category.query.all()
    return render_template(
        'index.html',
        featured_products=featured_products,
        trending_products=trending_products,
        sale_products=sale_products,
        categories=categories
    )

@app.route('/shop')
def catalog():
    query = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    brand = request.args.get('brand', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock_only = request.args.get('in_stock', type=bool)
    min_rating = request.args.get('rating', type=float)
    sort = request.args.get('sort', 'featured')
    page = request.args.get('page', 1, type=int)

    products_query = Product.query

    # Search filter
    if query:
        search_filter = or_(
            Product.name.ilike(f'%{query}%'),
            Product.brand.ilike(f'%{query}%'),
            Product.short_description.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Product.sku.ilike(f'%{query}%')
        )
        products_query = products_query.filter(search_filter)

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            products_query = products_query.filter(Product.category_id == selected_category.id)

    # Brand filter
    if brand:
        products_query = products_query.filter(Product.brand == brand)

    # Price range filter
    if min_price is not None:
        products_query = products_query.filter(Product.price >= min_price)
    if max_price is not None:
        products_query = products_query.filter(Product.price <= max_price)

    # In stock filter
    if in_stock_only:
        products_query = products_query.filter(Product.stock_quantity > 0)

    # Rating filter
    if min_rating is not None:
        products_query = products_query.filter(Product.rating_avg >= min_rating)

    # Sorting
    if sort == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())
    elif sort == 'newest':
        products_query = products_query.order_by(Product.created_at.desc())
    elif sort == 'rating':
        products_query = products_query.order_by(Product.rating_avg.desc())
    elif sort == 'name_asc':
        products_query = products_query.order_by(Product.name.asc())
    else:  # featured default
        products_query = products_query.order_by(Product.is_featured.desc(), Product.id.desc())

    # Pagination
    pagination = products_query.paginate(page=page, per_page=Config.ITEMS_PER_PAGE, error_out=False)
    products = pagination.items

    # Filter metadata for sidebar
    all_brands = [r[0] for r in db.session.query(Product.brand).distinct().order_by(Product.brand.asc()).all()]
    all_categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'shop/catalog.html',
        products=products,
        pagination=pagination,
        categories=all_categories,
        brands=all_brands,
        selected_category=selected_category,
        query=query,
        selected_brand=brand,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        min_rating=min_rating,
        current_sort=sort
    )

@app.route('/category/<slug>')
def category_view(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    return redirect(url_for('catalog', category=category.slug))

@app.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = WishlistItem.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).first() is not None

    review_form = ReviewForm()
    return render_template(
        'shop/product_detail.html',
        product=product,
        related_products=related_products,
        in_wishlist=in_wishlist,
        review_form=review_form
    )

@app.route('/api/search-suggest')
def search_suggest():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    results = Product.query.filter(
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.brand.ilike(f'%{query}%')
        )
    ).limit(6).all()

    data = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'brand': p.brand,
        'price': f"${p.price:.2f}",
        'image': p.primary_image,
        'category': p.category.name if p.category else ''
    } for p in results]
    return jsonify(data)

# ==========================================
# AUTHENTICATION & CUSTOMER ACCOUNT ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            is_admin=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Transfer guest cart items if any
        guest_id = session.get('guest_session_id')
        if guest_id:
            sync_guest_cart_to_user(guest_id, user.id)

        login_user(user)
        flash('Account created successfully! Welcome to VoltCart.', 'success')
        return redirect(url_for('index'))

    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.login_id.data.strip()
        user = User.query.filter(
            or_(
                User.email == login_input.lower(),
                User.username == login_input
            )
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            # Sync guest cart items
            guest_id = session.get('guest_session_id')
            if guest_id:
                sync_guest_cart_to_user(guest_id, user.id)

            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email/username or password. Please check your credentials.', 'danger')

    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    password_form = PasswordChangeForm()

    if 'submit_profile' in request.form and form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.postal_code = form.postal_code.data
        db.session.commit()
        flash('Your profile details have been updated.', 'success')
        return redirect(url_for('profile'))

    if 'submit_password' in request.form and password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'danger')

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template(
        'auth/profile.html',
        form=form,
        password_form=password_form,
        orders=orders
    )

@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('shop/my_orders.html', orders=orders)

@app.route('/order/<order_number>')
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id and (not current_user.is_authenticated or (current_user.id != order.user_id and not current_user.is_admin)):
        flash('You are not authorized to view this order invoice.', 'danger')
        return redirect(url_for('login', next=request.url))
    return render_template('shop/order_detail.html', order=order)

# ==========================================
# WISHLIST ROUTES
# ==========================================

@app.route('/wishlist')
@login_required
def wishlist():
    items = WishlistItem.query.filter_by(user_id=current_user.id).order_by(WishlistItem.created_at.desc()).all()
    return render_template('shop/wishlist.html', items=items)

@app.route('/api/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        in_wishlist = False
        message = f'{product.name} removed from your wishlist.'
    else:
        new_item = WishlistItem(user_id=current_user.id, product_id=product.id)
        db.session.add(new_item)
        db.session.commit()
        in_wishlist = True
        message = f'{product.name} added to your wishlist!'

    count = WishlistItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'in_wishlist': in_wishlist, 'count': count, 'message': message})

@app.route('/wishlist/move-to-cart/<int:product_id>', methods=['POST'])
@login_required
def wishlist_move_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    wishlist_item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        new_cart = CartItem(user_id=current_user.id, product_id=product.id, quantity=1)
        db.session.add(new_cart)
    db.session.commit()

    flash(f'Moved "{product.name}" to your shopping cart!', 'success')
    return redirect(url_for('wishlist'))

@app.route('/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def wishlist_remove(product_id):
    item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from wishlist.', 'info')
    return redirect(url_for('wishlist'))

# ==========================================
# CART & COUPON ROUTES
# ==========================================

@app.route('/cart')
def cart():
    guest_id = session.get('guest_session_id')
    coupon_code = session.get('applied_coupon')
    cart_data = get_cart_items_and_totals(
        user=current_user if current_user.is_authenticated else None,
        session_id=guest_id,
        coupon_code=coupon_code
    )
    coupon_form = CouponForm()
    return render_template('shop/cart.html', cart_data=cart_data, coupon_form=coupon_form)

@app.route('/api/cart/add', methods=['POST'])
def api_cart_add():
    data = request.get_json() or {}
    product_id = data.get('product_id') or request.form.get('product_id', type=int)
    quantity = data.get('quantity', 1) or request.form.get('quantity', 1)

    try:
        product_id = int(product_id)
        quantity = max(1, int(quantity))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid product or quantity'}), 400

    product = Product.query.get_or_404(product_id)
    if product.stock_quantity < 1:
        return jsonify({'success': False, 'message': 'Sorry, this product is currently out of stock.'}), 400

    if current_user.is_authenticated:
        item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if item:
            new_qty = min(product.stock_quantity, item.quantity + quantity)
            item.quantity = new_qty
        else:
            item = CartItem(user_id=current_user.id, product_id=product.id, quantity=min(product.stock_quantity, quantity))
            db.session.add(item)
    else:
        guest_id = get_guest_session_id()
        item = CartItem.query.filter_by(session_id=guest_id, product_id=product.id).first()
        if item:
            new_qty = min(product.stock_quantity, item.quantity + quantity)
            item.quantity = new_qty
        else:
            item = CartItem(session_id=guest_id, product_id=product.id, quantity=min(product.stock_quantity, quantity))
            db.session.add(item)

    db.session.commit()

    guest_id = session.get('guest_session_id')
    cart_data = get_cart_items_and_totals(
        user=current_user if current_user.is_authenticated else None,
        session_id=guest_id,
        coupon_code=session.get('applied_coupon')
    )

    return jsonify({
        'success': True,
        'message': f'"{product.name}" added to your cart!',
        'cart_count': cart_data['item_count'],
        'cart_total': format_currency(cart_data['total_amount']),
        'product_name': product.name,
        'product_image': product.primary_image
    })

@app.route('/api/cart/update', methods=['POST'])
def api_cart_update():
    data = request.get_json() or {}
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    if not item_id or quantity is None:
        return jsonify({'success': False, 'message': 'Invalid parameters'}), 400

    try:
        item_id = int(item_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid numbers'}), 400

    item = CartItem.query.get_or_404(item_id)
    if quantity <= 0:
        db.session.delete(item)
        db.session.commit()
    else:
        item.quantity = min(item.product.stock_quantity, quantity)
        db.session.commit()

    guest_id = session.get('guest_session_id')
    cart_data = get_cart_items_and_totals(
        user=current_user if current_user.is_authenticated else None,
        session_id=guest_id,
        coupon_code=session.get('applied_coupon')
    )

    item_subtotal = format_currency(item.subtotal) if quantity > 0 else '$0.00'

    return jsonify({
        'success': True,
        'cart_count': cart_data['item_count'],
        'item_subtotal': item_subtotal,
        'subtotal': format_currency(cart_data['subtotal']),
        'shipping_fee': format_currency(cart_data['shipping_fee']),
        'discount_amount': format_currency(cart_data['discount_amount']),
        'tax_amount': format_currency(cart_data['tax_amount']),
        'total_amount': format_currency(cart_data['total_amount'])
    })

@app.route('/api/cart/remove', methods=['POST'])
def api_cart_remove():
    data = request.get_json() or {}
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({'success': False, 'message': 'Invalid item ID'}), 400

    try:
        item_id = int(item_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid item ID'}), 400

    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    guest_id = session.get('guest_session_id')
    cart_data = get_cart_items_and_totals(
        user=current_user if current_user.is_authenticated else None,
        session_id=guest_id,
        coupon_code=session.get('applied_coupon')
    )

    return jsonify({
        'success': True,
        'message': 'Item removed from cart.',
        'cart_count': cart_data['item_count'],
        'subtotal': format_currency(cart_data['subtotal']),
        'shipping_fee': format_currency(cart_data['shipping_fee']),
        'discount_amount': format_currency(cart_data['discount_amount']),
        'tax_amount': format_currency(cart_data['tax_amount']),
        'total_amount': format_currency(cart_data['total_amount'])
    })

@app.route('/cart/apply-coupon', methods=['POST'])
def apply_coupon():
    form = CouponForm()
    if form.validate_on_submit():
        code = form.code.data.strip().upper()
        coupon = Coupon.query.filter_by(code=code).first()
        guest_id = session.get('guest_session_id')
        cart_data = get_cart_items_and_totals(
            user=current_user if current_user.is_authenticated else None,
            session_id=guest_id
        )

        if not coupon:
            flash(f'Coupon code "{code}" does not exist.', 'danger')
        else:
            is_valid, msg = coupon.is_valid(cart_data['subtotal'])
            if is_valid:
                session['applied_coupon'] = code
                flash(f'Coupon "{code}" applied successfully! You saved on this order.', 'success')
            else:
                flash(msg, 'danger')
    return redirect(url_for('cart'))

@app.route('/cart/remove-coupon', methods=['POST'])
def remove_coupon():
    session.pop('applied_coupon', None)
    flash('Coupon removed.', 'info')
    return redirect(url_for('cart'))

# ==========================================
# CHECKOUT & CASH ON DELIVERY (COD) ROUTES
# ==========================================

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    guest_id = session.get('guest_session_id')
    coupon_code = session.get('applied_coupon')
    cart_data = get_cart_items_and_totals(
        user=current_user if current_user.is_authenticated else None,
        session_id=guest_id,
        coupon_code=coupon_code
    )

    if not cart_data['items']:
        flash('Your shopping cart is currently empty. Please add products before checking out.', 'warning')
        return redirect(url_for('catalog'))

    form = CheckoutForm()

    # Pre-fill with current user info if available on GET
    if request.method == 'GET' and current_user.is_authenticated:
        form.customer_name.data = current_user.full_name or current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.shipping_address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.postal_code.data = current_user.postal_code

    if form.validate_on_submit():
        # Check stock availability for all items
        for item in cart_data['items']:
            if item.product.stock_quantity < item.quantity:
                flash(f'Sorry, "{item.product.name}" only has {item.product.stock_quantity} units in stock. Please adjust your cart.', 'danger')
                return redirect(url_for('cart'))

        # Create Order
        order_number = generate_order_number()
        order = Order(
            order_number=order_number,
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=form.customer_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            shipping_address=form.shipping_address.data.strip(),
            city=form.city.data.strip(),
            state=form.state.data.strip(),
            postal_code=form.postal_code.data.strip(),
            payment_method='Cash on Delivery',
            payment_status='Pending',
            order_status='Pending',
            subtotal=cart_data['subtotal'],
            shipping_fee=cart_data['shipping_fee'],
            discount_amount=cart_data['discount_amount'],
            tax_amount=cart_data['tax_amount'],
            total_amount=cart_data['total_amount'],
            coupon_code=coupon_code,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(order)
        db.session.flush()

        # Create Order Items & deduct stock
        for citem in cart_data['items']:
            oitem = OrderItem(
                order_id=order.id,
                product_id=citem.product_id,
                product_name=citem.product.name,
                product_image=citem.product.primary_image,
                price=citem.product.price,
                quantity=citem.quantity,
                subtotal=citem.subtotal
            )
            citem.product.stock_quantity -= citem.quantity
            db.session.add(oitem)
            db.session.delete(citem)

        # Clear session coupon
        session.pop('applied_coupon', None)
        db.session.commit()

        flash(f'Thank you! Your order {order.order_number} has been placed successfully.', 'success')
        return redirect(url_for('order_confirmation', order_number=order.order_number))

    return render_template('shop/checkout.html', form=form, cart_data=cart_data)

@app.route('/order-confirmation/<order_number>')
def order_confirmation(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('shop/order_confirmation.html', order=order)

# ==========================================
# REVIEWS
# ==========================================

@app.route('/product/<slug>/review', methods=['POST'])
@login_required
def submit_review(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    form = ReviewForm()

    if form.validate_on_submit():
        # Check if user already reviewed
        existing_review = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first()
        if existing_review:
            existing_review.rating = int(form.rating.data)
            existing_review.title = form.title.data.strip()
            existing_review.comment = form.comment.data.strip()
            flash('Your review has been updated.', 'info')
        else:
            # Check verified purchase
            has_bought = OrderItem.query.join(Order).filter(
                Order.user_id == current_user.id,
                OrderItem.product_id == product.id,
                Order.order_status.in_(['Shipped', 'Delivered', 'Processing'])
            ).first() is not None

            review = Review(
                product_id=product.id,
                user_id=current_user.id,
                rating=int(form.rating.data),
                title=form.title.data.strip(),
                comment=form.comment.data.strip(),
                verified_purchase=has_bought
            )
            db.session.add(review)
            flash('Thank you! Your review has been submitted.', 'success')

        db.session.commit()
        product.update_rating()
        db.session.commit()
    else:
        flash('Failed to submit review. Please fill all fields correctly.', 'danger')

    return redirect(url_for('product_detail', slug=product.slug))

# ==========================================
# ADMIN DASHBOARD & MANAGEMENT ROUTES
# ==========================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.payment_status == 'Paid').scalar() or 0.0
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(order_status='Pending').count()
    total_products = Product.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= 15).order_by(Product.stock_quantity.asc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    # Category product distribution for chart
    categories = Category.query.all()
    cat_labels = [c.name for c in categories]
    cat_counts = [len(c.products) for c in categories]

    return render_template(
        'admin/dashboard.html',
        total_revenue=total_revenue,
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_products=total_products,
        total_customers=total_customers,
        low_stock_products=low_stock_products,
        recent_orders=recent_orders,
        cat_labels=json.dumps(cat_labels),
        cat_counts=json.dumps(cat_counts)
    )

# --- Admin Products ---

@app.route('/admin/products')
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    cat_id = request.args.get('category_id', type=int)

    query = Product.query
    if search:
        query = query.filter(or_(Product.name.ilike(f'%{search}%'), Product.sku.ilike(f'%{search}%'), Product.brand.ilike(f'%{search}%')))
    if cat_id:
        query = query.filter(Product.category_id == cat_id)

    pagination = query.order_by(Product.id.desc()).paginate(page=page, per_page=Config.ADMIN_ITEMS_PER_PAGE, error_out=False)
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'admin/products.html',
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_cat=cat_id
    )

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    form = ProductForm()
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        slug = slugify(form.name.data)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = Product(
            name=form.name.data.strip(),
            slug=slug,
            brand=form.brand.data.strip(),
            category_id=form.category_id.data,
            price=form.price.data,
            original_price=form.original_price.data if form.original_price.data else None,
            stock_quantity=form.stock_quantity.data,
            sku=form.sku.data.strip(),
            short_description=form.short_description.data.strip() if form.short_description.data else None,
            description=form.description.data.strip() if form.description.data else None,
            specs_json=form.specs_json.data.strip() if form.specs_json.data else '{}',
            is_featured=form.is_featured.data,
            is_trending=form.is_trending.data,
            is_on_sale=form.is_on_sale.data
        )
        db.session.add(product)
        db.session.flush()

        # Add primary image
        primary_img = ProductImage(product_id=product.id, image_url=form.primary_image_url.data.strip(), is_primary=True)
        db.session.add(primary_img)

        # Add extra images
        if form.extra_images.data:
            urls = [u.strip() for u in form.extra_images.data.split('\n') if u.strip()]
            for u in urls:
                db.session.add(ProductImage(product_id=product.id, image_url=u, is_primary=False))

        db.session.commit()
        flash(f'Product "{product.name}" created successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', form=form, title='Add New Product')

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if request.method == 'GET':
        form.primary_image_url.data = product.primary_image
        extra_imgs = [img.image_url for img in product.images if not img.is_primary]
        form.extra_images.data = '\n'.join(extra_imgs)

    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.brand = form.brand.data.strip()
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.original_price = form.original_price.data if form.original_price.data else None
        product.stock_quantity = form.stock_quantity.data
        product.sku = form.sku.data.strip()
        product.short_description = form.short_description.data.strip() if form.short_description.data else None
        product.description = form.description.data.strip() if form.description.data else None
        product.specs_json = form.specs_json.data.strip() if form.specs_json.data else '{}'
        product.is_featured = form.is_featured.data
        product.is_trending = form.is_trending.data
        product.is_on_sale = form.is_on_sale.data

        # Re-sync images
        ProductImage.query.filter_by(product_id=product.id).delete()
        primary_img = ProductImage(product_id=product.id, image_url=form.primary_image_url.data.strip(), is_primary=True)
        db.session.add(primary_img)

        if form.extra_images.data:
            urls = [u.strip() for u in form.extra_images.data.split('\n') if u.strip()]
            for u in urls:
                db.session.add(ProductImage(product_id=product.id, image_url=u, is_primary=False))

        db.session.commit()
        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', form=form, product=product, title=f'Edit Product: {product.name}')

@app.route('/admin/products/delete/<int:id>', methods=['POST'])
@admin_required
def admin_product_delete(id):
    product = Product.query.get_or_404(id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" has been deleted.', 'info')
    return redirect(url_for('admin_products'))

# --- Admin Categories ---

@app.route('/admin/categories')
@admin_required
def admin_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_category_add():
    form = CategoryForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip() if form.slug.data else slugify(form.name.data)
        category = Category(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data.strip() if form.description.data else None,
            icon_class=form.icon_class.data.strip() if form.icon_class.data else 'fa-solid fa-microchip',
            image_url=form.image_url.data.strip() if form.image_url.data else None
        )
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{category.name}" created successfully.', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', form=form, title='Add Category')

@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_category_edit(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.slug = form.slug.data.strip() if form.slug.data else slugify(form.name.data)
        category.description = form.description.data.strip() if form.description.data else None
        category.icon_class = form.icon_class.data.strip() if form.icon_class.data else 'fa-solid fa-microchip'
        category.image_url = form.image_url.data.strip() if form.image_url.data else None
        db.session.commit()
        flash(f'Category "{category.name}" updated.', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', form=form, category=category, title=f'Edit Category: {category.name}')

@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@admin_required
def admin_category_delete(id):
    category = Category.query.get_or_404(id)
    if category.products:
        flash(f'Cannot delete category "{category.name}" because it contains {len(category.products)} products.', 'danger')
        return redirect(url_for('admin_categories'))
    name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{name}" has been deleted.', 'info')
    return redirect(url_for('admin_categories'))

# --- Admin Orders ---

@app.route('/admin/orders')
@admin_required
def admin_orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    search = request.args.get('q', '').strip()

    query = Order.query
    if status and status != 'all':
        query = query.filter(Order.order_status == status)
    if search:
        query = query.filter(or_(Order.order_number.ilike(f'%{search}%'), Order.customer_name.ilike(f'%{search}%'), Order.email.ilike(f'%{search}%')))

    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=Config.ADMIN_ITEMS_PER_PAGE, error_out=False)

    return render_template('admin/orders.html', orders=pagination.items, pagination=pagination, current_status=status, search=search)

@app.route('/admin/orders/<int:id>')
@admin_required
def admin_order_detail(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/orders/<int:id>/update-status', methods=['POST'])
@admin_required
def admin_order_update_status(id):
    order = Order.query.get_or_404(id)
    new_order_status = request.form.get('order_status')
    new_payment_status = request.form.get('payment_status')
    notes = request.form.get('notes')

    if new_order_status:
        order.order_status = new_order_status
        # If delivered and COD, auto mark paid
        if new_order_status == 'Delivered' and order.payment_method == 'Cash on Delivery':
            order.payment_status = 'Paid'

    if new_payment_status:
        order.payment_status = new_payment_status

    if notes is not None:
        order.notes = notes.strip()

    db.session.commit()
    flash(f'Order {order.order_number} status updated successfully.', 'success')
    return redirect(url_for('admin_order_detail', id=order.id))

# --- Admin Customers ---

@app.route('/admin/customers')
@admin_required
def admin_customers():
    customers = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=customers)

# ==========================================
# ERROR HANDLERS & APP ENTRY POINT
# ==========================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
