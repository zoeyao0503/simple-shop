import random
import string
import time

SITE_URL = 'https://snoocommerce.onrender.com'

PRODUCTS = [
    {'id': 1, 'name': 'Wireless Headphones', 'price': 79.99},
    {'id': 2, 'name': 'Minimalist Watch', 'price': 149.99},
    {'id': 3, 'name': 'Running Sneakers', 'price': 119.99},
    {'id': 4, 'name': 'Leather Backpack', 'price': 89.99},
    {'id': 5, 'name': 'Ceramic Mug Set', 'price': 34.99},
    {'id': 6, 'name': 'Desk Lamp', 'price': 59.99},
    {'id': 7, 'name': 'Bluetooth Speaker', 'price': 49.99},
    {'id': 8, 'name': 'Yoga Mat', 'price': 39.99},
    {'id': 9, 'name': 'Stainless Steel Water Bottle', 'price': 24.99},
    {'id': 10, 'name': 'Scented Candle Set', 'price': 29.99},
    {'id': 11, 'name': 'Wireless Earbuds', 'price': 59.99},
    {'id': 12, 'name': 'Cotton T-Shirt', 'price': 24.99},
    {'id': 13, 'name': 'French Press Coffee Maker', 'price': 34.99},
    {'id': 14, 'name': 'Sunglasses', 'price': 69.99},
    {'id': 15, 'name': 'Throw Blanket', 'price': 44.99},
    {'id': 16, 'name': 'Plant Pot Set', 'price': 27.99},
    {'id': 17, 'name': 'Mechanical Keyboard', 'price': 129.99},
    {'id': 18, 'name': 'Denim Jacket', 'price': 79.99},
    {'id': 19, 'name': 'Essential Oil Diffuser', 'price': 39.99},
    {'id': 20, 'name': 'Resistance Bands Set', 'price': 19.99},
    {'id': 21, 'name': 'Wireless Mouse', 'price': 34.99},
    {'id': 22, 'name': 'Linen Shirt', 'price': 54.99},
    {'id': 23, 'name': 'Cast Iron Skillet', 'price': 44.99},
    {'id': 24, 'name': 'Canvas Tote Bag', 'price': 22.99},
    {'id': 25, 'name': 'Face Moisturizer', 'price': 28.99},
    {'id': 26, 'name': 'Notebook Journal', 'price': 14.99},
    {'id': 27, 'name': 'Camping Hammock', 'price': 49.99},
    {'id': 28, 'name': 'Puzzle Game 1000pc', 'price': 18.99},
    {'id': 29, 'name': 'USB-C Hub', 'price': 39.99},
    {'id': 30, 'name': 'Wool Beanie', 'price': 19.99},
    {'id': 31, 'name': 'Chef Knife', 'price': 69.99},
    {'id': 32, 'name': 'Wall Clock', 'price': 42.99},
    {'id': 33, 'name': 'Lip Balm Set', 'price': 12.99},
    {'id': 34, 'name': 'Desk Organizer', 'price': 26.99},
    {'id': 35, 'name': 'Hiking Boots', 'price': 139.99},
    {'id': 36, 'name': 'Building Blocks Set', 'price': 29.99},
    {'id': 37, 'name': 'Portable Charger', 'price': 29.99},
    {'id': 38, 'name': 'Hoodie', 'price': 49.99},
    {'id': 39, 'name': 'Cutting Board Set', 'price': 32.99},
    {'id': 40, 'name': 'Leather Wallet', 'price': 49.99},
    {'id': 41, 'name': 'Hand Cream Set', 'price': 18.99},
    {'id': 42, 'name': 'Fountain Pen', 'price': 42.99},
    {'id': 43, 'name': 'Camping Lantern', 'price': 24.99},
    {'id': 44, 'name': 'Remote Control Car', 'price': 39.99},
    {'id': 45, 'name': 'Webcam HD', 'price': 54.99},
    {'id': 46, 'name': 'Chino Pants', 'price': 59.99},
    {'id': 47, 'name': 'Tea Kettle', 'price': 37.99},
    {'id': 48, 'name': 'Crossbody Bag', 'price': 44.99},
    {'id': 49, 'name': 'Facial Serum', 'price': 34.99},
    {'id': 50, 'name': 'Standing Desk Converter', 'price': 189.99},
    {'id': 51, 'name': 'Sleeping Bag', 'price': 79.99},
    {'id': 52, 'name': 'Board Game Classic', 'price': 24.99},
    {'id': 53, 'name': 'Smart Watch', 'price': 199.99},
    {'id': 54, 'name': 'Bomber Jacket', 'price': 89.99},
    {'id': 55, 'name': 'Blender', 'price': 64.99},
    {'id': 56, 'name': 'Belt', 'price': 29.99},
    {'id': 57, 'name': 'Sheet Mask Pack', 'price': 15.99},
    {'id': 58, 'name': 'Ergonomic Chair Cushion', 'price': 39.99},
    {'id': 59, 'name': 'Trekking Poles', 'price': 54.99},
    {'id': 60, 'name': 'Plush Stuffed Animal', 'price': 16.99},
    {'id': 61, 'name': 'Noise Machine', 'price': 44.99},
    {'id': 62, 'name': 'Flannel Shirt', 'price': 44.99},
    {'id': 63, 'name': 'Spice Rack', 'price': 27.99},
    {'id': 64, 'name': 'Watch Box', 'price': 34.99},
    {'id': 65, 'name': 'Sunscreen SPF 50', 'price': 16.99},
    {'id': 66, 'name': 'Monitor Stand', 'price': 49.99},
    {'id': 67, 'name': 'Cooler Bag', 'price': 34.99},
    {'id': 68, 'name': 'Card Game Party', 'price': 14.99},
    {'id': 69, 'name': 'Tablet Stand', 'price': 22.99},
    {'id': 70, 'name': 'Jogger Pants', 'price': 44.99},
    {'id': 71, 'name': 'Mixing Bowl Set', 'price': 29.99},
    {'id': 72, 'name': 'Silk Scarf', 'price': 39.99},
    {'id': 73, 'name': 'Body Lotion', 'price': 19.99},
    {'id': 74, 'name': 'Whiteboard', 'price': 34.99},
    {'id': 75, 'name': 'Portable Grill', 'price': 89.99},
    {'id': 76, 'name': 'Art Supply Kit', 'price': 34.99},
    {'id': 77, 'name': 'LED Strip Lights', 'price': 19.99},
    {'id': 78, 'name': 'Rain Jacket', 'price': 69.99},
    {'id': 79, 'name': 'Coffee Grinder', 'price': 44.99},
    {'id': 80, 'name': 'Baseball Cap', 'price': 19.99},
    {'id': 81, 'name': 'Hair Oil', 'price': 22.99},
    {'id': 82, 'name': 'Desk Calendar', 'price': 12.99},
    {'id': 83, 'name': 'Headlamp', 'price': 22.99},
    {'id': 84, 'name': 'Marble Run Kit', 'price': 27.99},
    {'id': 85, 'name': 'Wireless Charger', 'price': 24.99},
    {'id': 86, 'name': 'Polo Shirt', 'price': 34.99},
    {'id': 87, 'name': 'Toaster', 'price': 39.99},
    {'id': 88, 'name': 'Keychain Multitool', 'price': 14.99},
    {'id': 89, 'name': 'Bath Bomb Set', 'price': 21.99},
    {'id': 90, 'name': 'Sticky Notes Cube', 'price': 9.99},
    {'id': 91, 'name': 'Dry Bag', 'price': 19.99},
    {'id': 92, 'name': 'Play Dough Set', 'price': 12.99},
    {'id': 93, 'name': 'Monitor Light Bar', 'price': 44.99},
    {'id': 94, 'name': 'Swim Trunks', 'price': 29.99},
    {'id': 95, 'name': 'Baking Sheet Set', 'price': 24.99},
    {'id': 96, 'name': 'Umbrella', 'price': 24.99},
    {'id': 97, 'name': 'Exfoliating Scrub', 'price': 17.99},
    {'id': 98, 'name': 'Filing Cabinet', 'price': 129.99},
    {'id': 99, 'name': 'Compass', 'price': 14.99},
    {'id': 100, 'name': 'Kite', 'price': 17.99},
]

FAKE_USERS = [
    {'name': 'Alex Johnson', 'email': 'alex.johnson@example.com', 'phone': '5551234567'},
    {'name': 'Maria Garcia', 'email': 'maria.garcia@example.com', 'phone': '5552345678'},
    {'name': 'James Chen', 'email': 'james.chen@example.com', 'phone': '5553456789'},
    {'name': 'Sarah Williams', 'email': 'sarah.williams@example.com', 'phone': '5554567890'},
    {'name': 'David Kim', 'email': 'david.kim@example.com', 'phone': '5555678901'},
    {'name': 'Emily Brown', 'email': 'emily.brown@example.com', 'phone': '5556789012'},
    {'name': 'Carlos Rivera', 'email': 'carlos.rivera@example.com', 'phone': '5557890123'},
    {'name': 'Priya Patel', 'email': 'priya.patel@example.com', 'phone': '5558901234'},
]

USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.143 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.83',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]

IP_POOL = [
    '72.229.28.185',
    '98.137.11.164',
    '68.101.56.72',
    '209.95.50.14',
    '67.161.11.225',
    '65.60.160.210',
    '24.30.52.104',
    '71.198.1.42',
    '76.105.132.20',
    '24.150.170.80',
    '98.116.160.50',
    '71.40.128.18',
    '86.149.120.34',
    '126.78.200.12',
    '120.88.60.45',
    '49.37.152.18',
    '103.28.121.70',
]

PAGE_URLS = [
    f'{SITE_URL}/',
    f'{SITE_URL}/cart',
    f'{SITE_URL}/payment',
    f'{SITE_URL}/payment/success',
]


def random_user_agent():
    return random.choice(USER_AGENTS)


def random_ip():
    return random.choice(IP_POOL)


def random_user():
    return random.choice(FAKE_USERS).copy()


def random_products(min_count=1, max_count=3):
    count = random.randint(min_count, max_count)
    return random.sample(PRODUCTS, count)


def random_event_source_url(event_name, products=None):
    if event_name == 'ViewContent':
        if products:
            p = random.choice(products)
            return f'{SITE_URL}/product/{p["id"]}'
        return f'{SITE_URL}/'
    elif event_name == 'AddToCart':
        if products:
            p = random.choice(products)
            return random.choice([f'{SITE_URL}/product/{p["id"]}', f'{SITE_URL}/cart'])
        return random.choice([f'{SITE_URL}/', f'{SITE_URL}/cart'])
    elif event_name == 'Purchase':
        return f'{SITE_URL}/payment'
    elif event_name == 'Lead':
        return f'{SITE_URL}/payment'
    return f'{SITE_URL}/'


def random_fbclid():
    """fb.1.{unix_ms}.{62 alphanumeric chars}"""
    ts = int(time.time() * 1000)
    chars = string.ascii_letters + string.digits
    rand_part = ''.join(random.choices(chars, k=62))
    return f'fb.1.{ts}.{rand_part}'


def random_ttclid():
    """~26 alphanumeric characters"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=26))


def random_rdt_cid():
    """~19-digit numeric string"""
    return str(random.randint(10**18, 10**19 - 1))
