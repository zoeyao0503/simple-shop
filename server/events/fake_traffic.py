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

# Realistic user-agent strings covering Android, iOS, and desktop
USER_AGENTS = [
    # Android - Chrome
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.143 Mobile Safari/537.36',
    # iOS - Safari
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    # macOS - Chrome / Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    # Windows - Chrome / Edge / Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.83',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    # Linux - Chrome
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]

# Fake public IPs mapped to approximate city/region
IP_POOL = [
    '72.229.28.185',    # New York
    '98.137.11.164',    # Los Angeles
    '68.101.56.72',     # Chicago
    '209.95.50.14',     # Dallas
    '67.161.11.225',    # Seattle
    '65.60.160.210',    # Miami
    '24.30.52.104',     # Denver
    '71.198.1.42',      # San Francisco
    '76.105.132.20',    # Atlanta
    '24.150.170.80',    # Boston
    '98.116.160.50',    # Phoenix
    '71.40.128.18',     # Portland
    '86.149.120.34',    # London
    '126.78.200.12',    # Tokyo
    '120.88.60.45',     # Sydney
    '49.37.152.18',     # Mumbai
    '103.28.121.70',    # Singapore
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


def random_event_source_url(event_name):
    if event_name == 'ViewContent':
        return f'{SITE_URL}/'
    elif event_name == 'AddToCart':
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
