# VoltCart — Full-Stack Electronics E-Commerce Web Application

VoltCart is a modern, responsive full-stack electronics e-commerce web platform built with Python **Flask**, **SQLAlchemy**, **Jinja2**, **Bootstrap 5**, **FontAwesome 6**, and vanilla **JavaScript**.

---

## Key Features

### 🛒 Storefront & Catalog
- **Interactive Homepage**: Hero banner promo showcase, category quick-browse cards, flash deals with live countdown timers, trending gadgets, and trust badges.
- **Product Catalog (`/shop`)**: Multi-criteria filtering (by Category, Price range min/max, Brand, In-stock availability, Rating), keyword search with live AJAX auto-suggestions, and sort by Featured / Newest / Price / Rating.
- **Product Detail Pages (`/product/<slug>`)**:
  - Image gallery with interactive thumbnail switching.
  - Hardware specifications table (dynamically rendered from JSON).
  - Average ratings & verified purchase customer reviews.
  - In-stock availability limiter, instant "Add to Cart", and Wishlist toggle.
  - Review submission system with rating recalculation.

### 💳 Cart, Wishlist & Cash on Delivery (COD) Checkout
- **Smart Cart (`/cart`)**: Supports both guest sessions and logged-in users with automatic cart syncing upon login.
- **Dynamic Quantity Controls**: Increment/decrement quantity with instant asynchronous subtotal recalculation.
- **Promotional Coupon Vouchers**: Apply coupons (`WELCOME10`, `VOLT20`, `MEGA50`) with instant discount validation.
- **Customer Wishlist (`/wishlist`)**: Save favorite items, remove, or move directly to cart.
- **Cash on Delivery Checkout (`/checkout`)**: Streamlined address collection with user profile auto-fill, verified COD payment processing, unique order reference generation (`VC-2026-XXXXXX`), and printable receipts.

### 👤 Customer Accounts & Authentication
- **User Registration & Login**: Validated registration, email/username login, and password hashing via `werkzeug.security`.
- **Customer Profile (`/profile`)**: Manage shipping address book, update contact info, and change passwords.
- **Order History (`/my-orders` & `/order/<order_number>`)**: Real-time order milestone tracking (Order Received &rarr; Processing &rarr; Out for Delivery &rarr; Delivered) with full itemized receipt printing.

### 🛡️ Admin Dashboard & Control Panel (`/admin`)
- **Protected Admin Access**: Enforced with `@admin_required` decorator.
- **KPI Metrics & Analytics**: Total Revenue (COD collected), Total Orders, Catalog Items, Customer Count, and Category Share doughnut chart.
- **Low-Stock Alert Center**: Real-time warnings for items with &le; 15 units remaining.
- **Product Inventory CRUD**: Add, edit, delete products, manage multi-image galleries, and toggle promotional badges (Featured, Trending, On Sale).
- **Category Management**: Create, edit, and delete categories with associated product counters.
- **Order Fulfillment Center**: Inspect orders, update fulfillment status (Pending &rarr; Processing &rarr; Shipped &rarr; Delivered &rarr; Cancelled), update payment status, and manage courier notes.
- **Customer Directory**: View customer profiles, order history, and cumulative spend.

---

## Default Credentials

| Role | Email / Login | Password | Access Area |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@voltcart.com` (or `admin`) | `Admin@12345` | `/admin` & Storefront |
| **Demo Customer** | `user@voltcart.com` (or `alex_mercer`) | `User@12345` | Storefront & Checkout |

---

## Promotional Coupons Seeded

- `WELCOME10`: 10% off any order.
- `VOLT20`: 20% off orders over $150.00.
- `MEGA50`: $50.00 flat discount on orders over $300.00.

---

## Quickstart & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Database
```bash
python seed.py
```

### 3. Run Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

### 4. Run Automated Test Suite
```bash
python test_app.py
```
