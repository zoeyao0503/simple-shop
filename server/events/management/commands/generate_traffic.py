import copy
import hashlib
import json
import random
import time
import uuid
from datetime import datetime, timezone

import requests as http_requests
from django.conf import settings
from django.core.management.base import BaseCommand

from events.fake_traffic import (
    PRODUCTS,
    random_event_source_url,
    random_ip,
    random_products,
    random_user,
    random_user_agent,
)
from events.views import _append_log

META_GRAPH_API_URL = 'https://graph.facebook.com/v24.0/{pixel_id}/events'
TIKTOK_EVENTS_API_URL = 'https://business-api.tiktok.com/open_api/v1.3/pixel/track/'
REDDIT_CAPI_URL = 'https://ads-api.reddit.com/api/v2.0/conversions/events/{account_id}'

EVENT_MAP = {
    'ViewContent': {'meta': 'ViewContent', 'tiktok': 'ViewContent', 'reddit': 'ViewContent'},
    'AddToCart':   {'meta': 'AddToCart',   'tiktok': 'AddToCart',   'reddit': 'AddToCart'},
    'Purchase':    {'meta': 'Purchase',    'tiktok': 'CompletePayment', 'reddit': 'Purchase'},
}

REDDIT_TRACKING_TYPE = {
    'ViewContent': 'ViewContent',
    'AddToCart':   'AddToCart',
    'Purchase':    'Purchase',
}


def platform_event_name(event_name, platform):
    entry = EVENT_MAP.get(event_name, {})
    return entry.get(platform, event_name)

EVENT_WEIGHTS = [
    ('ViewContent', 50),
    ('AddToCart', 30),
    ('Purchase', 20),
]
EVENT_NAMES = [name for name, _ in EVENT_WEIGHTS]
EVENT_CUMULATIVE = []
_total = 0
for _name, _weight in EVENT_WEIGHTS:
    _total += _weight
    EVENT_CUMULATIVE.append(_total)

PRODUCT_NAME_MAP = {str(p['id']): p['name'] for p in PRODUCTS}


def pick_event_name():
    r = random.randint(1, EVENT_CUMULATIVE[-1])
    for i, threshold in enumerate(EVENT_CUMULATIVE):
        if r <= threshold:
            return EVENT_NAMES[i]
    return EVENT_NAMES[-1]


def _send_to_tiktok(event_data, products):
    if not settings.TIKTOK_ACCESS_TOKEN:
        return None, None

    event_name = event_data['event_name']
    tt_event = platform_event_name(event_name, 'tiktok')
    user_data = event_data.get('user_data', {})
    custom_data = event_data.get('custom_data', {})

    contents = [
        {
            'content_id': str(p['id']),
            'content_type': 'product',
            'content_name': p['name'],
        }
        for p in products
    ]

    tt_user = {}
    em_list = user_data.get('em', [])
    if em_list:
        tt_user['email'] = em_list[0] if isinstance(em_list, list) else em_list
    ph_list = user_data.get('ph', [])
    if ph_list:
        tt_user['phone_number'] = ph_list[0] if isinstance(ph_list, list) else ph_list

    tt_context = {
        'user_agent': user_data.get('client_user_agent', ''),
        'ip': user_data.get('client_ip_address', ''),
        'page': {
            'url': event_data.get('event_source_url', ''),
        },
    }
    if tt_user:
        tt_context['user'] = tt_user

    tt_payload = {
        'pixel_code': settings.TIKTOK_PIXEL_ID,
        'event': tt_event,
        'event_id': event_data.get('event_id', ''),
        'timestamp': datetime.fromtimestamp(
            event_data.get('event_time', int(time.time())), tz=timezone.utc
        ).strftime('%Y-%m-%dT%H:%M:%S%z'),
        'context': tt_context,
        'properties': {
            'contents': contents,
            'currency': custom_data.get('currency', 'USD'),
            'value': custom_data.get('value', 0),
        },
    }

    headers = {
        'Content-Type': 'application/json',
        'Access-Token': settings.TIKTOK_ACCESS_TOKEN,
    }

    try:
        resp = http_requests.post(TIKTOK_EVENTS_API_URL, json=tt_payload, headers=headers, timeout=10)
        result = resp.json()
        return resp.status_code, result
    except Exception as e:
        return 500, {'error': str(e)}


def _send_to_reddit(event_data, products):
    if not settings.REDDIT_ACCESS_TOKEN:
        return None, None

    event_name = event_data['event_name']
    tracking_type = REDDIT_TRACKING_TYPE.get(event_name)
    if not tracking_type:
        return None, None

    user_data = event_data.get('user_data', {})
    custom_data = event_data.get('custom_data', {})

    event_at = datetime.fromtimestamp(
        event_data.get('event_time', int(time.time())), tz=timezone.utc
    ).strftime('%Y-%m-%dT%H:%M:%SZ')

    reddit_event = {
        'event_at': event_at,
        'event_type': {
            'tracking_type': tracking_type,
        },
    }

    event_metadata = {}
    event_id = event_data.get('event_id')
    if event_id:
        event_metadata['conversion_id'] = event_id
    if custom_data.get('value') is not None:
        event_metadata['value'] = int(round(custom_data['value'] * 100))
    if custom_data.get('currency'):
        event_metadata['currency'] = custom_data['currency']
    rdt_products = [
        {
            'id': str(p['id']),
            'name': p['name'],
            'category': 'product',
        }
        for p in products
    ]
    if rdt_products:
        event_metadata['products'] = rdt_products
        event_metadata['item_count'] = len(rdt_products)
    if event_metadata:
        reddit_event['event_metadata'] = event_metadata

    user = {}
    email_list = user_data.get('em', [])
    if email_list:
        user['email'] = email_list[0] if isinstance(email_list, list) else email_list
    phone_list = user_data.get('ph', [])
    if phone_list:
        user['external_id'] = phone_list[0] if isinstance(phone_list, list) else phone_list
    ip = user_data.get('client_ip_address')
    if ip:
        user['ip_address'] = hashlib.sha256(ip.encode()).hexdigest()
    ua = user_data.get('client_user_agent')
    if ua:
        user['user_agent'] = ua
    if user:
        reddit_event['user'] = user

    url = REDDIT_CAPI_URL.format(account_id=settings.REDDIT_PIXEL_ID)
    payload = {'events': [reddit_event]}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.REDDIT_ACCESS_TOKEN}',
    }

    try:
        resp = http_requests.post(url, json=payload, headers=headers, timeout=10)
        result = resp.json()
        return resp.status_code, result
    except Exception as e:
        return 500, {'error': str(e)}


class Command(BaseCommand):
    help = 'Generate synthetic traffic for Meta CAPI, TikTok Events API, and Reddit CAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=100,
            help='Number of events to send (default: 100)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Build payloads but do not POST to APIs',
        )

    def handle(self, *args, **options):
        count = options['count']
        dry_run = options['dry_run']

        if not settings.META_ACCESS_TOKEN:
            self.stderr.write(self.style.ERROR('META_ACCESS_TOKEN is not set'))
            return

        meta_url = META_GRAPH_API_URL.format(pixel_id=settings.META_PIXEL_ID)
        counters = {'ViewContent': 0, 'AddToCart': 0, 'Purchase': 0}
        errors = 0

        self.stdout.write(f'Generating {count} synthetic events (dry_run={dry_run})...')

        for i in range(count):
            event_name = pick_event_name()
            counters[event_name] = counters.get(event_name, 0) + 1

            user = random_user()
            products = random_products()
            event_id = str(uuid.uuid4())

            event_data = {
                'event_name': event_name,
                'event_time': int(time.time()),
                'event_id': event_id,
                'action_source': 'website',
                'event_source_url': random_event_source_url(event_name),
                'user_data': {
                    'client_user_agent': random_user_agent(),
                    'client_ip_address': random_ip(),
                    'em': [hashlib.sha256(user['email'].lower().strip().encode()).hexdigest()],
                    'ph': [hashlib.sha256(user['phone'].strip().encode()).hexdigest()],
                },
                'custom_data': {
                    'content_type': 'product',
                    'content_ids': [str(p['id']) for p in products],
                    'content_names': [p['name'] for p in products],
                    'currency': 'USD',
                    'value': round(sum(p['price'] for p in products), 2),
                },
            }

            if dry_run:
                self.stdout.write(f'  [{i+1}/{count}] {event_name} (dry-run) id={event_id[:8]}...')
                continue

            # --- Meta CAPI (strip em/ph — no PII to Meta) ---
            meta_sanitized = copy.deepcopy(event_data)
            meta_ud = meta_sanitized.get('user_data', {})
            for pii_key in ('em', 'ph', 'email', 'phone'):
                meta_ud.pop(pii_key, None)
            meta_payload = {
                'data': json.dumps([meta_sanitized]),
                'access_token': settings.META_ACCESS_TOKEN,
            }

            meta_ok = True
            try:
                resp = http_requests.post(meta_url, data=meta_payload, timeout=10)
                meta_result = resp.json()
                meta_status = resp.status_code
                if meta_status != 200:
                    meta_ok = False
            except Exception as e:
                meta_status = 500
                meta_result = {'error': str(e)}
                meta_ok = False

            # --- TikTok Events API ---
            tt_status, tt_result = _send_to_tiktok(event_data, products)

            # --- Reddit Conversions API ---
            rdt_status, rdt_result = _send_to_reddit(event_data, products)

            log_entry = {
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'event_name': event_name,
                'event_id': event_id,
                'payload_sent': event_data,
                'meta_status_code': meta_status,
                'meta_response': meta_result,
                'source': 'generate_traffic',
            }
            if tt_status is not None:
                log_entry['tiktok_status_code'] = tt_status
                log_entry['tiktok_response'] = tt_result
            if rdt_status is not None:
                log_entry['reddit_status_code'] = rdt_status
                log_entry['reddit_response'] = rdt_result
            _append_log(log_entry)

            if not meta_ok:
                errors += 1
                self.stderr.write(f'  [{i+1}/{count}] {event_name} META FAILED {meta_status}: {meta_result}')
            else:
                tt_info = ''
                if tt_status is not None:
                    tt_info = f' | TT:{tt_status}'
                rdt_info = ''
                if rdt_status is not None:
                    rdt_info = f' | RDT:{rdt_status}'
                self.stdout.write(f'  [{i+1}/{count}] {event_name} OK id={event_id[:8]}...{tt_info}{rdt_info}')

            if i < count - 1:
                time.sleep(0.1)

        summary_parts = [f'{v} {k}' for k, v in counters.items() if v > 0]
        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Sent {count} events ({", ".join(summary_parts)}). Errors: {errors}'
        ))
