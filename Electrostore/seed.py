import json
from datetime import datetime, timedelta
from flask import Flask
from config import Config
from models import db, User, Category, Product, ProductImage, Review, Coupon, Order, OrderItem
from utils import generate_order_number

def seed_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        print("Creating database schema...")
        db.drop_all()
        db.create_all()

        print("Seeding Users...")
        admin = User(
            username='admin', email='admin@voltcart.com',
            full_name='VoltCart System Admin', phone='+1 (800) 555-0199',
            address='100 Innovation Way, Suite 400', city='San Francisco',
            state='CA', postal_code='94105', is_admin=True
        )
        admin.set_password('Admin@12345')

        customer = User(
            username='alex_mercer', email='user@voltcart.com',
            full_name='Alex Mercer', phone='+1 (555) 234-5678',
            address='742 Evergreen Terrace', city='San Jose',
            state='CA', postal_code='95134', is_admin=False
        )
        customer.set_password('User@12345')

        customer2 = User(
            username='sarah_connor', email='sarah@example.com',
            full_name='Sarah Connor', phone='+1 (555) 987-6543',
            address='456 Cyberdyne Blvd', city='Los Angeles',
            state='CA', postal_code='90001', is_admin=False
        )
        customer2.set_password('User@12345')

        db.session.add_all([admin, customer, customer2])
        db.session.commit()

        print("Seeding Categories...")
        categories_data = [
            {'name': 'Smartphones & Tablets', 'slug': 'smartphones-tablets', 'description': 'Flagship smartphones, 5G tablets, and premium mobile devices.', 'icon_class': 'fa-solid fa-mobile-screen-button', 'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Laptops & Computers', 'slug': 'laptops-computers', 'description': 'Ultra-fast ultrabooks, powerful workstations, and compact mini PCs.', 'icon_class': 'fa-solid fa-laptop', 'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Audio & Headphones', 'slug': 'audio-headphones', 'description': 'Noise-canceling headphones, studio monitors, and wireless earbuds.', 'icon_class': 'fa-solid fa-headphones', 'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Smart Home & IoT', 'slug': 'smart-home-iot', 'description': 'Automated lighting, security hubs, smart thermostats, and voice assistants.', 'icon_class': 'fa-solid fa-house-signal', 'image_url': 'https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Gaming & Consoles', 'slug': 'gaming-consoles', 'description': 'Next-gen gaming consoles, mechanical keyboards, OLED displays, and VR gear.', 'icon_class': 'fa-solid fa-gamepad', 'image_url': 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Wearables & Smartwatches', 'slug': 'wearables-smartwatches', 'description': 'Fitness trackers, titanium smartwatches, and biometric wearables.', 'icon_class': 'fa-solid fa-clock', 'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Cameras & Drones', 'slug': 'cameras-drones', 'description': 'Full-frame mirrorless cameras, 4K aerial drones, and cinematic lenses.', 'icon_class': 'fa-solid fa-camera', 'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80'},
            {'name': 'Accessories & Cables', 'slug': 'accessories-cables', 'description': 'GaN fast chargers, Thunderbolt 4 docks, MagSafe mounts, and rugged cables.', 'icon_class': 'fa-solid fa-plug', 'image_url': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&auto=format&fit=crop&q=80'}
        ]

        cat_map = {}
        for cdata in categories_data:
            cat = Category(**cdata)
            db.session.add(cat)
            db.session.flush()
            cat_map[cdata['slug']] = cat

        db.session.commit()

        print("Seeding Products batch 1...")
        products_data = [
            {
                'name': 'VoltPhone 15 Pro Max 512GB Titanium',
                'slug': 'voltphone-15-pro-max-512gb-titanium',
                'brand': 'VoltCore',
                'category_slug': 'smartphones-tablets',
                'price': 1199.99,
                'original_price': 1299.99,
                'stock_quantity': 35,
                'sku': 'VP-15PM-TIT-512',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'Super Retina XDR OLED 120Hz display with aerospace-grade titanium frame and A18 Bionic chip.',
                'description': 'The VoltPhone 15 Pro Max represents the pinnacle of mobile engineering. Built with a lightweight aerospace titanium chassis, custom action button, and a revolutionary 48MP triple-lens optical system with 5x telephoto zoom. Offers all-day battery life, Wi-Fi 7 connectivity, and next-generation AI processing.',
                'specs': {'Display': '6.7-inch Super Retina XDR OLED (120Hz ProMotion)', 'Processor': 'Octa-core Neural Bionic A18 Chip', 'Storage': '512GB UFS 4.0', 'RAM': '12GB LPDDR5X', 'Camera': '48MP Main + 12MP Ultra-Wide + 12MP 5x Telephoto', 'Battery': '4,850 mAh with 45W Fast Charging', 'Water Resistance': 'IP68', 'Weight': '221g'},
                'images': [
                    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'name': 'NovaTab Ultra 13 Pro AMOLED Tablet',
                'slug': 'novatab-ultra-13-pro-amoled-tablet',
                'brand': 'NovaTech',
                'category_slug': 'smartphones-tablets',
                'price': 899.99,
                'original_price': 999.99,
                'stock_quantity': 22,
                'sku': 'NT-TAB13-AMO-256',
                'is_featured': True,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': '13.2-inch 144Hz Dynamic AMOLED 2X workstation tablet with low-latency stylus included.',
                'description': 'Elevate your creative and multitasking workflow with the NovaTab Ultra 13. Engineered with an ultra-thin 5.5mm aluminum armor frame, quad AKG speakers with Dolby Atmos, and seamless desktop mode for multi-window productivity.',
                'specs': {'Display': '13.2-inch Dynamic AMOLED 2X (2880x1920, 144Hz)', 'Processor': 'Snapdragon 8 Gen 3', 'Storage': '256GB SSD', 'RAM': '12GB', 'Stylus': 'NovaPen Pro Included', 'Battery': '11,200 mAh'},
                'images': [
                    'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'name': 'PixelStream Fold 5G Dual Display',
                'slug': 'pixelstream-fold-5g-dual-display',
                'brand': 'PixelStream',
                'category_slug': 'smartphones-tablets',
                'price': 1599.99,
                'original_price': 1799.99,
                'stock_quantity': 14,
                'sku': 'PS-FOLD-5G-512',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'Zero-crease fluid foldable smartphone unfolding into a tablet-sized 7.8-inch display.',
                'description': 'Unfold endless possibilities with PixelStream Fold. Built with a fluid waterdrop titanium hinge, ultra-thin flexible glass, and split-screen multitasking tools that make productivity feel effortless on the go.',
                'specs': {'Inner Display': '7.8-inch LTPO OLED 120Hz', 'Cover Display': '6.4-inch OLED', 'Processor': 'Tensor G4 AI Co-Processor', 'Storage': '512GB', 'RAM': '16GB', 'Camera': '50MP Triple Camera'},
                'images': ['https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'ZenithBook Pro 16 M3 Max Studio',
                'slug': 'zenithbook-pro-16-m3-max-studio',
                'brand': 'ApexCompute',
                'category_slug': 'laptops-computers',
                'price': 2499.99,
                'original_price': 2699.99,
                'stock_quantity': 18,
                'sku': 'ZB-PRO16-M3M-36G',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': False,
                'short_description': 'Liquid Retina XDR mini-LED display with 16-core CPU, 40-core GPU, and 36GB unified memory.',
                'description': 'The ultimate workstation powerhouse for 3D creators, developers, and audio engineers. Featuring up to 22 hours of continuous battery life, whisper-quiet thermal architecture, 1000 nits sustained HDR brightness, and a studio-quality 6-speaker spatial audio system.',
                'specs': {'Display': '16.2-inch Liquid Retina XDR (3456x2234, 120Hz)', 'Processor': '16-Core M3 Max (40-core GPU)', 'RAM': '36GB Unified Memory', 'Storage': '1TB NVMe PCIe 4.0 SSD', 'Battery': 'Up to 22 Hours', 'Weight': '2.14 kg'},
                'images': [
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80'
                ]
            }
        ]

        products_data.extend([
            {
                'name': 'AeroBlade 14 Ultra-Slim OLED Laptop',
                'slug': 'aeroblade-14-ultra-slim-oled-laptop',
                'brand': 'Aero',
                'category_slug': 'laptops-computers',
                'price': 1349.99,
                'original_price': 1499.99,
                'stock_quantity': 25,
                'sku': 'AB-14-OLED-32G',
                'is_featured': False,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': '14-inch 2.8K 120Hz Lumina OLED touchscreen weighing only 1.18kg with Intel Core Ultra 7.',
                'description': 'Featherlight precision meets heavyweight performance. The AeroBlade 14 is crafted from CNC-machined magnesium-aluminum alloy and features an Intel AI Boost NPU for accelerated offline workflow, Copilot keys, and an edge-to-edge glass haptic touchpad.',
                'specs': {'Display': '14.0-inch 2.8K OLED (2880x1800)', 'Processor': 'Intel Core Ultra 7 155H', 'RAM': '32GB LPDDR5X', 'Storage': '1TB Gen4 SSD', 'Weight': '1.18 kg'},
                'images': ['https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'HyperStation X Mini PC Workstation',
                'slug': 'hyperstation-x-mini-pc-workstation',
                'brand': 'ApexCompute',
                'category_slug': 'laptops-computers',
                'price': 799.99,
                'original_price': 899.99,
                'stock_quantity': 40,
                'sku': 'HS-MINI-R9-64G',
                'is_featured': False,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': 'Ultra-compact 0.8-liter aluminum cube PC powered by AMD Ryzen 9 8945HS with dual 2.5G LAN.',
                'description': 'A pocket-sized powerhouse designed for clean desktop setups, home servers, and multimedia editing stations. Delivers 8-core desktop-class speeds while drawing under 65W of power with whisper-quiet vapor chamber cooling.',
                'specs': {'Processor': 'AMD Ryzen 9 8945HS (8 Cores, 16 Threads)', 'Graphics': 'Radeon 780M', 'RAM': '32GB DDR5', 'Storage': '1TB M.2 NVMe SSD', 'Networking': 'Dual 2.5GbE LAN + Wi-Fi 6E'},
                'images': ['https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'SonicPulse Master ANC Wireless Headphones',
                'slug': 'sonicpulse-master-anc-wireless-headphones',
                'brand': 'SonicPulse',
                'category_slug': 'audio-headphones',
                'price': 349.99,
                'original_price': 399.99,
                'stock_quantity': 45,
                'sku': 'SP-ANC-MST-BLK',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'Industry-leading adaptive active noise cancellation with 40mm custom graphene drivers and 60hr battery.',
                'description': 'Immerse yourself in acoustic perfection. The SonicPulse Master features real-time adaptive noise cancellation with 8 acoustic microphones, LDAC high-resolution lossless streaming, memory foam ear cushions covered in vegan leather, and multi-point Bluetooth pairing.',
                'specs': {'Drivers': '40mm Graphene Diaphragm', 'ANC': 'Adaptive Hybrid ANC (-45dB)', 'Battery': '60 Hours (ANC Off)', 'Codecs': 'LDAC, AAC, aptX Adaptive', 'Weight': '255g'},
                'images': [
                    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'name': 'VoltPods Pro 2 True Wireless Earbuds',
                'slug': 'voltpods-pro-2-true-wireless-earbuds',
                'brand': 'VoltCore',
                'category_slug': 'audio-headphones',
                'price': 199.99,
                'original_price': 229.99,
                'stock_quantity': 60,
                'sku': 'VP-POD2-WHT',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': False,
                'short_description': 'Lossless spatial audio earbuds with transparency mode, skin-detect sensor, and wireless charging case.',
                'description': 'Designed for seamless daily sound. VoltPods Pro 2 delivers studio acoustics in a pocketable design, boasting dynamic head tracking spatial audio, crystal-clear beamforming call microphones, and IP54 dust and splash resistance.',
                'specs': {'Drivers': '11mm Custom Woofer', 'ANC': 'Adaptive Active Noise Cancellation', 'Battery': '6 Hours + 30 Hours Case', 'Water Resistance': 'IP54'},
                'images': ['https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'EchoStudio 360 Hi-Res Smart Speaker',
                'slug': 'echostudio-360-hi-res-smart-speaker',
                'brand': 'SonicPulse',
                'category_slug': 'audio-headphones',
                'price': 229.99,
                'original_price': 279.99,
                'stock_quantity': 28,
                'sku': 'ES-360-SPK-GRY',
                'is_featured': False,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': 'Immersive 3D room-filling acoustics with 5 directional drivers and automatic room calibration.',
                'description': 'Experience your favorite music the way the artist intended. EchoStudio 360 automatically analyzes the acoustics of your room and fine-tunes playback for optimal spatial audio distribution across any space.',
                'specs': {'Power': '330W Peak Class-D', 'Speakers': '5.25\" Subwoofer + 3 Midranges + 1 Tweeter', 'Connectivity': 'Wi-Fi 6, Bluetooth 5.2, AirPlay 2'},
                'images': ['https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80']
            }
        ])

        products_data.extend([
            {
                'name': 'VoltHub Prime Smart Home Bridge & Security Base',
                'slug': 'volthub-prime-smart-home-bridge-security-base',
                'brand': 'VoltCore',
                'category_slug': 'smart-home-iot',
                'price': 149.99,
                'original_price': 179.99,
                'stock_quantity': 32,
                'sku': 'VH-PRIME-HUB-01',
                'is_featured': False,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'Matter and Thread universal smart home gateway with local offline automations and 128-bit encryption.',
                'description': 'Unify every smart device under one roof. The VoltHub Prime connects Zigbee, Z-Wave, Matter, and Thread devices to Apple HomeKit, Google Home, and Home Assistant seamlessly without cloud latency.',
                'specs': {'Protocols': 'Matter over Thread, Zigbee 3.0, Z-Wave Plus, Wi-Fi 6', 'Security': '128-bit AES Local Storage', 'Siren': '105dB Built-in'},
                'images': ['https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'OmniView 4K Solar Security Camera Set (2-Pack)',
                'slug': 'omniview-4k-solar-security-camera-set-2pack',
                'brand': 'OmniGuard',
                'category_slug': 'smart-home-iot',
                'price': 299.99,
                'original_price': 349.99,
                'stock_quantity': 20,
                'sku': 'OG-CAM4K-SOLAR-2P',
                'is_featured': True,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': 'Wire-free 4K HDR outdoor cameras with integrated solar panels, color night vision, and AI human detection.',
                'description': 'Protect your perimeter effortlessly without ever changing batteries. Featuring continuous solar trickle charging, dual spotlights, two-way audio, and local microSD encrypted storage with zero monthly subscriptions.',
                'specs': {'Resolution': '4K UHD HDR (3840x2160)', 'Power': 'Integrated Solar Panel + 10,000mAh Battery', 'Night Vision': 'Color Night Vision with Dual Spotlights'},
                'images': ['https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'Vortex Stealth OLED 34-inch Curved Gaming Monitor',
                'slug': 'vortex-stealth-oled-34-inch-curved-gaming-monitor',
                'brand': 'VortexGaming',
                'category_slug': 'gaming-consoles',
                'price': 899.99,
                'original_price': 1099.99,
                'stock_quantity': 15,
                'sku': 'VX-OLED34-240HZ',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'UWQHD Quantum Dot OLED display with 240Hz refresh rate, 0.03ms response time, and 1800R curve.',
                'description': 'Immerse yourself in breathtaking infinite contrast and lightning-fast pixel response. Features AMD FreeSync Premium Pro, NVIDIA G-Sync compatibility, custom heatsink design with fanless cooling to prevent burn-in, and RGB ambient bias lighting.',
                'specs': {'Screen': '34-inch QD-OLED (3440x1440 UWQHD)', 'Refresh Rate': '240Hz (0.03ms GtG)', 'Curvature': '1800R', 'HDR': 'DisplayHDR True Black 400'},
                'images': ['https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'Vortex Elite Pro Wireless Controller',
                'slug': 'vortex-elite-pro-wireless-controller',
                'brand': 'VortexGaming',
                'category_slug': 'gaming-consoles',
                'price': 129.99,
                'original_price': 149.99,
                'stock_quantity': 50,
                'sku': 'VX-CTRL-ELITE-BLK',
                'is_featured': False,
                'is_trending': True,
                'is_on_sale': False,
                'short_description': 'Hall-effect magnetic anti-drift joysticks with hair-trigger locks and 4 remappable rear paddles.',
                'description': 'Engineered for tournament esports dominance. Equipped with frictionless magnetic Hall Effect thumbsticks that will never develop stick drift, tactile mechanical microswitches on the D-pad and ABXY buttons, and 40-hour rechargeable battery.',
                'specs': {'Joysticks': 'Hall Effect Magnetic (Anti-Drift)', 'Switches': 'Mechanical Microswitches', 'Battery Life': '40 Hours'},
                'images': ['https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'CyberDeck RGB Wireless Hot-Swap Mechanical Keyboard',
                'slug': 'cyberdeck-rgb-wireless-hot-swap-mechanical-keyboard',
                'brand': 'VortexGaming',
                'category_slug': 'gaming-consoles',
                'price': 159.99,
                'original_price': 189.99,
                'stock_quantity': 38,
                'sku': 'CD-KB75-RGB-HOT',
                'is_featured': False,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': 'Gasket-mounted 75% layout keyboard with factory-lubed linear switches and programmable OLED screen.',
                'description': 'Enjoy satisfying creamy keystrokes and whisper acoustics. Built with double-shot PBT keycaps, per-key RGB backlighting, tri-mode wireless connectivity, and an aluminum CNC volume rotary dial.',
                'specs': {'Layout': '75% Compact Gasket Mount', 'Switches': 'Volt Fox Linear (Hot-Swappable)', 'Keycaps': 'Double-Shot PBT', 'Battery': '4,000 mAh'},
                'images': ['https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80']
            }
        ])

        products_data.extend([
            {
                'name': 'VoltWatch Ultra Titanium Cellular 49mm',
                'slug': 'voltwatch-ultra-titanium-cellular-49mm',
                'brand': 'VoltCore',
                'category_slug': 'wearables-smartwatches',
                'price': 699.99,
                'original_price': 799.99,
                'stock_quantity': 24,
                'sku': 'VW-ULTRA-TIT-49',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'Rugged grade-5 titanium smartwatch with dual-frequency GPS, depth gauge, ECG, and 3000-nit sapphire screen.',
                'description': 'Built for extreme endurance athletes, divers, and adventurers. Features EN13319 scuba dive certification, emergency SOS siren, heart rate variability tracking, sleep apnea detection, and up to 72 hours in low-power mode.',
                'specs': {'Case': '49mm Grade 5 Titanium', 'Display': '1.99\" OLED (3,000 nits)', 'GPS': 'Dual-Frequency L1/L5', 'Water Rating': '100m / Dive EN13319', 'Battery': '36 to 72 Hours'},
                'images': ['https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'PulseFit Active Health & Sleep Smart Ring',
                'slug': 'pulsefit-active-health-sleep-smart-ring',
                'brand': 'PulseFit',
                'category_slug': 'wearables-smartwatches',
                'price': 249.99,
                'original_price': 279.99,
                'stock_quantity': 42,
                'sku': 'PF-RING-GEN3-TIT',
                'is_featured': False,
                'is_trending': True,
                'is_on_sale': False,
                'short_description': 'Featherweight 3-gram titanium ring tracking sleep stages, recovery, temperature trends, and stress 24/7.',
                'description': 'Screen-free health insights discreetly on your finger. Waterproof up to 100m, with 7-day battery life on a single 45-minute charge and zero subscription fees required.',
                'specs': {'Material': 'Titanium PVD Coated', 'Sensors': 'Infrared PPG, Temp, 3D Accelerometer', 'Battery': '6-8 Days', 'Water Resistance': '10 ATM (100m)'},
                'images': ['https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'AeroCam CineDrone 8K Hasselblad Gimbal',
                'slug': 'aerocam-cinedrone-8k-hasselblad-gimbal',
                'brand': 'AeroCam',
                'category_slug': 'cameras-drones',
                'price': 1799.99,
                'original_price': 1999.99,
                'stock_quantity': 12,
                'sku': 'AC-DRONE-8K-PRO',
                'is_featured': True,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': 'Foldable 8K/60fps cinematic drone with 4/3 CMOS sensor, omnidirectional obstacle sensing, and 45min flight.',
                'description': 'Capture breathtaking Hollywood-grade aerial footage. Features a 10-bit D-Log M color profile, up to 15km O4 video transmission range, and intelligent MasterShots autonomous flight tracking modes.',
                'specs': {'Camera': '4/3 CMOS 20MP Hasselblad 8K', 'Flight Time': '46 Minutes', 'Range': '15km O4 Video', 'Sensing': 'Omnidirectional APAS 5.0'},
                'images': ['https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'LuminaFX 4K Vlogging Mirrorless Camera',
                'slug': 'luminafx-4k-vlogging-mirrorless-camera',
                'brand': 'LuminaOptics',
                'category_slug': 'cameras-drones',
                'price': 899.99,
                'original_price': 999.99,
                'stock_quantity': 19,
                'sku': 'LF-CAM-VLOG-4K',
                'is_featured': False,
                'is_trending': True,
                'is_on_sale': False,
                'short_description': '24.2MP APS-C mirrorless camera with vari-angle flip touchscreen, real-time eye autofocus, and 4K60p.',
                'description': 'Engineered for next-gen creators. Packed with a large 24.2MP Exmor sensor, background defocus button, directional 3-capsule microphone with windscreen included, and seamless USB webcam streaming.',
                'specs': {'Sensor': '24.2MP APS-C Exmor', 'Video': '4K HDR at 60fps', 'Autofocus': '425 Phase-Detect AF Points', 'Audio': 'Directional 3-Capsule Mic'},
                'images': ['https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'VoltCharge 140W GaN 4-Port Fast Charger',
                'slug': 'voltcharge-140w-gan-4-port-fast-charger',
                'brand': 'VoltCore',
                'category_slug': 'accessories-cables',
                'price': 79.99,
                'original_price': 99.99,
                'stock_quantity': 85,
                'sku': 'VC-GAN140-4P',
                'is_featured': True,
                'is_trending': True,
                'is_on_sale': True,
                'short_description': 'Gallium Nitride PD 3.1 ultra-compact desktop charger capable of fast-charging two laptops simultaneously.',
                'description': 'Say goodbye to bulky power bricks. Utilizes cutting-edge Navitas GaNFast chips to deliver 140W single-port USB-C Power Delivery 3.1 in a size 40% smaller than conventional chargers with advanced thermal protection.',
                'specs': {'Output': '140W Max PD 3.1', 'Ports': '3x USB-C + 1x USB-A', 'Technology': 'GaN III', 'Weight': '290g'},
                'images': ['https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'ThunderDock Pro 14-in-1 Dual 4K Docking Station',
                'slug': 'thunderdock-pro-14-in-1-dual-4k-docking-station',
                'brand': 'ApexCompute',
                'category_slug': 'accessories-cables',
                'price': 189.99,
                'original_price': 219.99,
                'stock_quantity': 30,
                'sku': 'TD-14IN1-TB4-HUB',
                'is_featured': False,
                'is_trending': False,
                'is_on_sale': True,
                'short_description': 'Thunderbolt 4 / USB4 aluminum hub with 96W host charging, dual HDMI 2.1, 2.5G LAN, and SD 4.0 card reader.',
                'description': 'Transform your laptop into an uncompromising desktop studio with a single cable. Features an integrated aluminum heat sink, dual display outputs at 4K 120Hz or single 8K 60Hz, and high-speed 10Gbps USB 3.2 data transfer.',
                'specs': {'Host': 'Thunderbolt 4 / USB4 (96W PD)', 'Video': '2x HDMI 2.1 + 1x DP 1.4', 'Ports': '5x USB 10Gbps, SD/microSD, 2.5G LAN'},
                'images': ['https://images.unsplash.com/photo-1544652478-6653e09f18a2?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'MagMount Orbit 3-in-1 Magnetic Wireless Stand',
                'slug': 'magmount-orbit-3-in-1-magnetic-wireless-stand',
                'brand': 'VoltCore',
                'category_slug': 'accessories-cables',
                'price': 89.99,
                'original_price': 109.99,
                'stock_quantity': 55,
                'sku': 'MM-ORBIT-3IN1-SLV',
                'is_featured': False,
                'is_trending': True,
                'is_on_sale': False,
                'short_description': 'Weighted CNC aluminum stand charging phone, smartwatch, and wireless earbuds concurrently with 15W MagSafe.',
                'description': 'Clean up your nightstand or workspace. Features high-strength N52 neodymium magnets, floating elevation design for landscape StandBy viewing, and an integrated LED soft ambient night light.',
                'specs': {'Phone Charger': '15W Qi2 MagSafe', 'Watch Charger': '5W Fast Watch Puck', 'Base': '5W Earbuds Pad', 'Material': 'Anodized Aluminum'},
                'images': ['https://images.unsplash.com/photo-1622445262464-84b1456045b6?w=800&auto=format&fit=crop&q=80']
            },
            {
                'name': 'ArmoredFlex Braided 240W USB-C to USB-C Cable (2m)',
                'slug': 'armoredflex-braided-240w-usb-c-cable-2m',
                'brand': 'VoltCore',
                'category_slug': 'accessories-cables',
                'price': 24.99,
                'original_price': 29.99,
                'stock_quantity': 120,
                'sku': 'AF-C2C-240W-2M',
                'is_featured': False,
                'is_trending': False,
                'is_on_sale': False,
                'short_description': 'Kevlar-reinforced ballistic nylon cable supporting 240W Power Delivery and 40Gbps data sync.',
                'description': 'Built to withstand 35,000+ extreme bends. Features gold-plated connectors, built-in E-marker intelligent safety chip, and premium aluminum alloy housing.',
                'specs': {'Power': '240W PD 3.1 (48V/5A)', 'Speed': 'USB4 / 40Gbps', 'Length': '2.0m (6.6ft)', 'Durability': 'Kevlar 35k+ Bend Rating'},
                'images': ['https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&auto=format&fit=crop&q=80']
            }
        ])

        created_products = []
        for pdata in products_data:
            cat = cat_map[pdata['category_slug']]
            images = pdata.pop('images')
            cat_slug = pdata.pop('category_slug')
            specs = pdata.pop('specs')

            prod = Product(category_id=cat.id, **pdata)
            prod.specs = specs
            db.session.add(prod)
            db.session.flush()

            for idx, img_url in enumerate(images):
                img = ProductImage(product_id=prod.id, image_url=img_url, is_primary=(idx == 0))
                db.session.add(img)

            created_products.append(prod)

        db.session.commit()

        print("Seeding Reviews...")
        reviews_data = [
            {'idx': 0, 'user': customer, 'rating': 5, 'title': 'Unbelievable performance and titanium finish!', 'comment': 'The switch from aluminum to titanium makes a huge difference in hand feel. The 5x telephoto camera is crisp even in low light.'},
            {'idx': 0, 'user': customer2, 'rating': 5, 'title': 'Best phone on the market hands down.', 'comment': 'Battery easily lasts 2 full days of moderate use. The screen brightness outdoors in bright sunlight is fantastic.'},
            {'idx': 3, 'user': customer, 'rating': 5, 'title': 'Absolute workhorse for 4K video rendering.', 'comment': 'Exports 4K ProRes timeline in minutes with zero fan noise. The Liquid Retina XDR screen is color accurate right out of the box.'},
            {'idx': 6, 'user': customer2, 'rating': 5, 'title': 'Noise cancellation is pure black silence.', 'comment': 'Used these on a 14-hour flight. Blocked out all engine roar completely. Soundstage is wide and punchy.'},
            {'idx': 7, 'user': customer, 'rating': 4, 'title': 'Great daily drivers with deep bass.', 'comment': 'Fits snugly during gym workouts and running. Microphone clarity on Zoom calls is remarkably clear.'},
            {'idx': 11, 'user': customer2, 'rating': 5, 'title': 'The true black levels in games are mindblowing.', 'comment': 'Going from IPS to OLED at 240Hz is a night and day difference. Colors pop and there is zero ghosting in competitive shooters.'},
            {'idx': 14, 'user': customer, 'rating': 5, 'title': 'Tough as nails, GPS is pinpoint accurate.', 'comment': 'Took this on a 3-day backcountry trail. Tracked my hike, elevation, and oxygen saturation without needing a recharge.'}
        ]

        for rdata in reviews_data:
            prod = created_products[rdata['idx']]
            rev = Review(
                product_id=prod.id,
                user_id=rdata['user'].id,
                rating=rdata['rating'],
                title=rdata['title'],
                comment=rdata['comment'],
                verified_purchase=True
            )
            db.session.add(rev)

        db.session.commit()

        for prod in created_products:
            prod.update_rating()
        db.session.commit()

        print("Seeding Coupons...")
        coupons_data = [
            {'code': 'WELCOME10', 'discount_percent': 10.0, 'discount_amount': 0.0, 'min_order_amount': 0.0, 'is_active': True, 'expires_at': datetime.utcnow() + timedelta(days=365)},
            {'code': 'VOLT20', 'discount_percent': 20.0, 'discount_amount': 0.0, 'min_order_amount': 150.0, 'is_active': True, 'expires_at': datetime.utcnow() + timedelta(days=180)},
            {'code': 'MEGA50', 'discount_percent': 0.0, 'discount_amount': 50.0, 'min_order_amount': 300.0, 'is_active': True, 'expires_at': datetime.utcnow() + timedelta(days=90)}
        ]

        for cp in coupons_data:
            c = Coupon(**cp)
            db.session.add(c)
        db.session.commit()

        print("Seeding Sample Orders...")
        order1 = Order(
            order_number=generate_order_number(),
            user_id=customer.id,
            customer_name=customer.full_name,
            email=customer.email,
            phone=customer.phone,
            shipping_address=customer.address,
            city=customer.city,
            state=customer.state,
            postal_code=customer.postal_code,
            payment_method='Cash on Delivery',
            payment_status='Paid',
            order_status='Delivered',
            subtotal=349.99,
            shipping_fee=0.0,
            tax_amount=28.00,
            discount_amount=0.0,
            total_amount=377.99,
            notes='Please ring doorbell upon delivery.',
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        db.session.add(order1)
        db.session.flush()

        item1 = OrderItem(
            order_id=order1.id,
            product_id=created_products[6].id,
            product_name=created_products[6].name,
            product_image=created_products[6].primary_image,
            price=349.99,
            quantity=1,
            subtotal=349.99
        )
        db.session.add(item1)

        order2 = Order(
            order_number=generate_order_number(),
            user_id=customer.id,
            customer_name=customer.full_name,
            email=customer.email,
            phone=customer.phone,
            shipping_address=customer.address,
            city=customer.city,
            state=customer.state,
            postal_code=customer.postal_code,
            payment_method='Cash on Delivery',
            payment_status='Pending',
            order_status='Processing',
            subtotal=1279.98,
            shipping_fee=0.0,
            tax_amount=92.16,
            discount_amount=127.99,
            total_amount=1244.15,
            coupon_code='WELCOME10',
            notes='Leave by the front porch if not home.',
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(order2)
        db.session.flush()

        item2_1 = OrderItem(
            order_id=order2.id,
            product_id=created_products[0].id,
            product_name=created_products[0].name,
            product_image=created_products[0].primary_image,
            price=1199.99,
            quantity=1,
            subtotal=1199.99
        )
        item2_2 = OrderItem(
            order_id=order2.id,
            product_id=created_products[18].id,
            product_name=created_products[18].name,
            product_image=created_products[18].primary_image,
            price=79.99,
            quantity=1,
            subtotal=79.99
        )
        db.session.add_all([item2_1, item2_2])
        db.session.commit()
        print("[SUCCESS] Database seeded completely!")

if __name__ == '__main__':
    seed_database()
