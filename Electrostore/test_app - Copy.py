import unittest
import json
from app import app
from models import db, User, Product, Category, Order, CartItem, WishlistItem, Coupon

class VoltCartFullStackTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_homepage_and_catalog(self):
        """Test storefront homepage and catalog endpoints"""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Volt', resp.data)
        self.assertIn(b'Cart', resp.data)

        # Shop catalog
        resp = self.client.get('/shop')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Explore Electronics', resp.data)

    def test_02_search_and_filters(self):
        """Test search query, category filtering, and live suggest API"""
        # Search for VoltPhone
        resp = self.client.get('/shop?q=VoltPhone')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'VoltPhone 15 Pro Max', resp.data)

        # Category filter
        resp = self.client.get('/shop?category=laptops-computers')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'ZenithBook Pro', resp.data)

        # Search suggest API
        resp = self.client.get('/api/search-suggest?q=OLED')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(len(data) > 0)
        self.assertIn('name', data[0])

    def test_03_product_detail(self):
        """Test single product detail page"""
        with app.app_context():
            prod = Product.query.first()
            slug = prod.slug
            name = prod.name

        resp = self.client.get(f'/product/{slug}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(name.encode('utf-8'), resp.data)
        self.assertIn(b'Hardware Specifications', resp.data)

    def test_04_cart_and_coupon_flow(self):
        """Test AJAX cart addition, coupon validation, quantity update"""
        with app.app_context():
            prod = Product.query.filter(Product.stock_quantity > 0).first()
            prod_id = prod.id

        # 1. Add to Cart via API
        resp = self.client.post('/api/cart/add', json={'product_id': prod_id, 'quantity': 1})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)

        # 2. View Cart Page
        resp = self.client.get('/cart')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Your Shopping Cart', resp.data)

        # 3. Apply Promo Coupon
        resp = self.client.post('/cart/apply-coupon', data={'code': 'WELCOME10'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'WELCOME10', resp.data)

    def test_05_auth_and_profile_flow(self):
        """Test customer registration, login, profile view, and logout"""
        # Register new user
        test_email = 'test_tester@example.com'
        resp = self.client.post('/register', data={
            'username': 'tester99',
            'email': test_email,
            'full_name': 'Test Tester',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Log in as test customer
        resp = self.client.post('/login', data={
            'login_id': test_email,
            'password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Access Profile
        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Test Tester', resp.data)

        # Logout
        resp = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_06_cash_on_delivery_checkout(self):
        """Test complete Cash on Delivery checkout and order generation"""
        with app.app_context():
            prod = Product.query.first()
            prod_id = prod.id
            init_stock = prod.stock_quantity

        # Add to cart
        self.client.post('/api/cart/add', json={'product_id': prod_id, 'quantity': 1})

        # Checkout form submission
        resp = self.client.post('/checkout', data={
            'customer_name': 'David Miller',
            'email': 'david@example.com',
            'phone': '+1 (555) 777-8899',
            'shipping_address': '88 Silicon Park Ave',
            'city': 'Palo Alto',
            'state': 'CA',
            'postal_code': '94301',
            'notes': 'Call when outside'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Order Successfully Placed!', resp.data)
        self.assertIn(b'Cash on Delivery', resp.data)

        # Verify stock decreased
        with app.app_context():
            updated_prod = Product.query.get(prod_id)
            self.assertEqual(updated_prod.stock_quantity, init_stock - 1)

    def test_07_admin_dashboard_and_product_management(self):
        """Test admin security decorator, admin login, and management endpoints"""
        # Non-logged-in access to /admin should redirect to login
        resp = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        # Login as Admin
        resp = self.client.post('/login', data={
            'login_id': 'admin@voltcart.com',
            'password': 'Admin@12345'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Admin Dashboard
        resp = self.client.get('/admin')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Analytics & Store Metrics', resp.data)

        # Admin Products List
        resp = self.client.get('/admin/products')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Products & Hardware Inventory', resp.data)

        # Admin Orders List
        resp = self.client.get('/admin/orders')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Customer Orders & Tracking', resp.data)

        # Admin Customers List
        resp = self.client.get('/admin/customers')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Registered Customer Directory', resp.data)

if __name__ == '__main__':
    unittest.main()
