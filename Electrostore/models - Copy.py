import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'is_admin': self.is_admin
        }

    def __repr__(self):
        return f'<User {self.username} (Admin={self.is_admin})>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon_class = db.Column(db.String(100), default='fa-solid fa-microchip')
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    @property
    def product_count(self):
        return len(self.products)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(280), unique=True, nullable=False, index=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    short_description = db.Column(db.String(350), nullable=True)
    description = db.Column(db.Text, nullable=True)
    specs_json = db.Column(db.Text, nullable=True)  # JSON string dictionary
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    is_trending = db.Column(db.Boolean, default=False, index=True)
    is_on_sale = db.Column(db.Boolean, default=False, index=True)
    rating_avg = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def specs(self):
        if not self.specs_json:
            return {}
        try:
            return json.loads(self.specs_json)
        except Exception:
            return {}

    @specs.setter
    def specs(self, value):
        if isinstance(value, dict):
            self.specs_json = json.dumps(value)
        elif isinstance(value, str):
            self.specs_json = value
        else:
            self.specs_json = '{}'

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(round(((self.original_price - self.price) / self.original_price) * 100))
        return 0

    @property
    def primary_image(self):
        for img in self.images:
            if img.is_primary:
                return img.image_url
        if self.images:
            return self.images[0].image_url
        return 'https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=600&auto=format&fit=crop&q=80'

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def update_rating(self):
        valid_reviews = [r for r in self.reviews if r.rating]
        if valid_reviews:
            self.rating_count = len(valid_reviews)
            self.rating_avg = round(sum(r.rating for r in valid_reviews) / self.rating_count, 1)
        else:
            self.rating_count = 0
            self.rating_avg = 0.0

    def __repr__(self):
        return f'<Product {self.name} (${self.price})>'


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ProductImage {self.id} (Prod {self.product_id})>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def subtotal(self):
        return round(self.product.price * self.quantity, 2) if self.product else 0.0

    def __repr__(self):
        return f'<CartItem Prod={self.product_id} Qty={self.quantity}>'


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uq_user_product_wishlist'),
    )

    def __repr__(self):
        return f'<WishlistItem User={self.user_id} Prod={self.product_id}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Customer Details
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)

    # Shipping Address
    shipping_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)

    # Financials & Status
    payment_method = db.Column(db.String(50), default='Cash on Delivery', nullable=False)
    payment_status = db.Column(db.String(50), default='Pending', nullable=False)  # Pending, Paid, Failed
    order_status = db.Column(db.String(50), default='Pending', nullable=False)    # Pending, Processing, Shipped, Delivered, Cancelled
    
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    shipping_fee = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    coupon_code = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @property
    def status_badge_class(self):
        mapping = {
            'Pending': 'warning',
            'Processing': 'info',
            'Shipped': 'primary',
            'Delivered': 'success',
            'Cancelled': 'danger'
        }
        return mapping.get(self.order_status, 'secondary')

    @property
    def payment_badge_class(self):
        mapping = {
            'Pending': 'warning',
            'Paid': 'success',
            'Failed': 'danger'
        }
        return mapping.get(self.payment_status, 'secondary')

    def __repr__(self):
        return f'<Order {self.order_number} (${self.total_amount})>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_image = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    # Relationship to product
    product = db.relationship('Product', backref='order_items', lazy=True)

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    title = db.Column(db.String(120), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    verified_purchase = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review Product={self.product_id} Rating={self.rating}>'


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    discount_percent = db.Column(db.Float, default=0.0)  # e.g., 10 for 10%
    discount_amount = db.Column(db.Float, default=0.0)   # fixed $ amount off
    min_order_amount = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def is_valid(self, subtotal=0.0):
        if not self.is_active:
            return False, "This coupon is no longer active."
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False, "This coupon has expired."
        if subtotal < self.min_order_amount:
            return False, f"Minimum order amount of ${self.min_order_amount:.2f} required for this coupon."
        return True, "Valid"

    def calculate_discount(self, subtotal):
        valid, msg = self.is_valid(subtotal)
        if not valid:
            return 0.0
        if self.discount_percent > 0:
            return round((self.discount_percent / 100.0) * subtotal, 2)
        elif self.discount_amount > 0:
            return min(round(self.discount_amount, 2), subtotal)
        return 0.0

    def __repr__(self):
        return f'<Coupon {self.code} ({self.discount_percent}% off)>'