import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'voltcart-super-secret-key-2026-xyz894')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'voltcart.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 12
    ADMIN_ITEMS_PER_PAGE = 15
    CURRENCY_SYMBOL = '$'
    STORE_NAME = 'VoltCart'
    STORE_EMAIL = 'support@voltcart.com'
    STORE_PHONE = '+1 (800) 865-8227'
    STORE_ADDRESS = '742 Evergreen Terrace, Silicon Valley, CA 94025'
    FREE_SHIPPING_THRESHOLD = 99.00
    STANDARD_SHIPPING_FEE = 9.99
    TAX_RATE = 0.08  # 8% sales tax